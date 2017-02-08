#!/usr/bin/env python

from gasmeter_sqlite3 import SQLite3Prcessor
import time
from datetime import datetime
import sys
import sqlite3
import getopt
import logging
import logging.config
import rrdtool

epoch = datetime.utcfromtimestamp(0)

def main(argv):

    # configure 
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    global log
    log = logging.getLogger(__name__)

    log.info('reading args')
    log.debug('args: '+str(argv))

    try:                                
        opts, args = getopt.getopt(argv, "hr:", ["help","rrd="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:                
        if opt == '-h':
            usage();
            sys.exit(0)
        elif (opt in ("-r", "--rrd")):
            convert_db_to_rrd(arg)

def usage():
    print """
Usage:
    -h                   -   print this message
    -r <db file name>    -   the file name of the sqlite3 db
    """
    
def unix_time_millis(dt):
    return (dt - epoch).total_seconds() # * 1000.0

def convert_db_to_rrd(db_name):
    db_proc = SQLite3Prcessor(db_name)
    db_proc.setup()

    rrd_name=db_name+".rrd"

    try:
        rrdtool.create(
            rrd_name,
            '--no-overwrite',
            '--step', '60',
            '--start', '-1y',
            'DS:counter:GAUGE:86400:0:100000',
            'DS:consum:ABSOLUTE:86400:0:1',
            'RRA:LAST:0.5:1:4320',
            'RRA:AVERAGE:0.5:1:4320',
            'RRA:LAST:0.5:1440:30',
            'RRA:AVERAGE:0.5:1440:30',
            'RRA:LAST:0.5:10080:520',
            'RRA:AVERAGE:0.5:10080:520')
    except rrdtool.OperationalError:
        log.warn(rrd_name+" already exists")

    result = db_proc.get_content()
    for r in result:
        dt = datetime.strptime(r[1],'%Y-%m-%d %H:%M:%S.%f')
        try:
            rrdtool.update(rrd_name, str(int(unix_time_millis(dt)))+':'+str(r[2])+':0.01')#, r[1]))
        except rrdtool.OperationalError:
            pass

    for sched in ['daily' , 'weekly', 'monthly']:
        if sched == 'weekly':
            period = 'w'
        elif sched == 'daily':
            period = 'd'
        elif sched == 'monthly':
            period = 'm'
        ret = rrdtool.graph( "%s-%s.png" %(sched,rrd_name), "--start", "-1%s" %(period), "--vertical-label=Num",
            "-w 800",
            "-h 400",
            "DEF:consum=gasmeter.rrd:consum:AVERAGE",
            "CDEF:conph=consum,3600,*,24,*",
            "LINE2:conph#00FF00:m^3/h" )


if __name__ == "__main__":
    main(sys.argv[1:])




