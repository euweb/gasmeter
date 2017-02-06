#!/usr/bin/env python

import sqlite3
import time
from datetime import datetime
import logging


#############
#
#   SQLite3 DB Prozessor
#
#
class SQLite3Prcessor:        

    #db default name
    _db = "gasmeter-example.db"

    _conn = None

    #log = logging.getLogger(__name__)

    def __init__(self, db, log=None):
        if(db is not None):
            self._db = db
        #global log
        self.log = log or logging.getLogger(__name__)

    def __del__(self):
        if self._conn is not None:
            self._conn.close()

    def setup(self):
        # create db if needed
        self.log.debug('initializing db: ' + self._db)
        print('hier')
        self._conn = sqlite3.connect(self._db, check_same_thread=False)
        self._conn.isolation_level = None # -> autocommit
        self._conn.execute("""
        CREATE TABLE IF NOT EXISTS gas_meter(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date DATETIME NOT NULL,
          value REAL NOT NULL,
          type INTEGER
        );
        """)

    def get_current_max(self):
     
        cursor = self._conn.cursor()

        # preselect counter value
        current = cursor.execute("SELECT value FROM gas_meter ORDER BY id DESC LIMIT 1;")
        cur_counter = current.fetchone()
        counter = None
        if cur_counter is not None:
            self.log.debug("loading current counter value from database: "+str(cur_counter[0]))
            counter = float(cur_counter[0])

        cursor.close()
        return counter


    def update(self, counter, time, type):
        self.log.debug("updateing counter: " + str(time) + ", type: " + str(type) + ", value: " + str(counter))
        cursor = self._conn.cursor()
        cursor.execute("insert into gas_meter (id, date, value, type) values (null,?,?,?)", (time, counter, type) )
        cursor.close()


    def print_db(self):
        cursor = self._conn.cursor()
        # show contents of the TABLE
        cursor.execute("select * from gas_meter;")
        result = cursor.fetchall()
        for r in result:
            print(r)
        cursor.close()



def main():    

    logging.basicConfig(level=logging.DEBUG)
    global log
    log = logging.getLogger()

    counter = None
    
    proc = SQLite3Prcessor(None)
    proc.setup()

    proc.print_db()

    counter = proc.get_current_max()
    if counter is None:
        counter = 0.0

    counter += 0.01

    proc.update(counter,format(str(datetime.now())),1)
    done = False
    while not done:

        try:

            counter += 0.01
            proc.update(counter,format(str(datetime.now())),0)
            time.sleep(1)

        except KeyboardInterrupt:
            done = True

if __name__ == "__main__":
    main()




