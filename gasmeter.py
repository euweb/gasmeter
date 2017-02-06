#!/usr/bin/env python

import time
from datetime import datetime
from gasmeter_sqlite3 import SQLite3Prcessor
import sys
import sqlite3
import getopt
import RPi.GPIO as GPIO
import logging
import logging.config

# Pin 18 (GPIO 24)
PIN=18
#log=None

def main(argv):

    counter = None 
    dbname = None

    # configure 
    logging.config.fileConfig('logging.conf')
    global log
    log = logging.getLogger(__name__)

    log.info('reading args')
    log.debug('args: '+str(argv))

    try:                                
        opts, args = getopt.getopt(argv, "hd:c:", ["help","db","counter="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:                
        if opt == '-h':
            usage();
            sys.exit(0)
        elif (opt in ("-d", "--db")):
            dbname = arg
        elif (opt in ("-c", "--counter")): 
            try:
                counter = float(arg)
            except ValueError:
                log.error("counter not a number")
                sys.exit(2)               

    configuration = GPIOConfiguration(PIN)
    cb = GPIOCallback(configuration)

    if dbname is not None:

        db_proc = SQLite3Prcessor(dbname)
        db_proc.setup()

        # try to get counter from database, if no counter was defined
        if counter is None:
            log.info("get counter from database")
            counter = db_proc.get_current_max()
            log.debug("db counter: "+str(counter))
        
        cb.register(db_proc)

    try:
         cb.start(counter)
         done = False
         while not done:
             log.info("alive: current: " + str(cb.get_current()))
             time.sleep(10)
    except KeyboardInterrupt:
         done = True

def usage():
    print """
Usage:
    -h                   -   print this message
    -d <db file name>    -   the file name of the sqlite3 db
    -c <counter value>   -   initial value for the counter (step is always 0.01)
    """


class GPIOConfiguration:

    def __init__(self, pin):
        self._pin = pin

    def setup(self, callback):
        log.info("setup GPIO configuration")
        # setup for raspberry pi 2 B
        # RPi.GPIO board layout
        GPIO.setmode(GPIO.BOARD)
        # Pin PIN as input, pull-up (3.3V)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._pin, GPIO.FALLING, callback=callback, bouncetime=2000)
        

    def tear_down(self):
        log.info("tear down GPIO configuration")
        GPIO.remove_event_detect(_pin)
        GPIO.cleanup()
        

    def current(self):
        return GPIO.input(_pin)


class GPIOCallback:
    counter = None
    def __init__(self, configuration):
        self.subscribers = set()
        self.configuration = configuration
        self.first_event = True

    def start(self, init_counter):
        log.info("starting event listening on gpio")
        self.counter = init_counter
        self.configuration.setup(self.on_impulse)

    def stop(self):
        log.info("stoping event listening on gpio")
        self.configuration.tear_down()

    def register(self,who):
        self.subscribers.add(who)

    def unregister(self,who):
        self.subscribers.discard(who)

    def get_current(self):
        return self.counter        

    def on_impulse(self,channel):
        self.counter += 0.01
        now = str(datetime.now())
        type = (2,1)[self.first_event]
        self.first_event = False
        log.debug('update: '+str(self.counter)+" "+str(now)+" "+str(type))
        for subscriber in self.subscribers:
            subscriber.update(self.counter,now,type)

if __name__ == "__main__":
    main(sys.argv[1:])




