"""
This module defines ``MongoTailer``, a class that can be instantiated to
follow MongoDB and and to invoke a callback with the contents of its
latest CRUD operations.

The strategy employed is to open a tailable cursor on the MongoDB oplog.
This is suggested in the `MongoDB documentation 
<http://www.mongodb.org/display/DOCS/Tailable+Cursors>`_.

Usage example:

::

    def printer(next):
        print(next)

    dbconn = pymongo.Connection()

    MongoTailer(
        dbconn=dbconn,
        callback=printer,
    ).start()
"""


import tornado, tornado.ioloop
import pymongo
import logging, datetime

ioloop = tornado.ioloop.IOLoop.instance()

class MongoTailer(object):
    """
    Follows the MongoDB oplog and invokes ``callback`` with the results
    in real time. 
    """
    def __init__(self, dbconn, callback):
        self.latest = None
        self.cursor = None
        self.dbconn = dbconn
        self.callback = callback
        self.ioloop_handler = None

    def start(self):
        """
        Ensures the cursor is open and start the loop that will manage
        following the cursor.
        """
        logging.debug("In start()")
        self.redefine_cursor()

        if not self.ioloop_handler:
            self.ioloop_handler = ioloop.add_callback(self.get_next)

    def _get_last(self):
        """
        Returns the last object on the oplog so that we can begin listening
        from here by sorting by its _id field.
        """
        lasts = self.dbconn.local.oplog.rs.find({
            "o._id": {"$exists": True}
        }, sort=[("$natural", pymongo.DESCENDING),], limit=1)
        
        last = lasts.next()
        logging.debug("Last item is %s" % last)
        return last

    def redefine_cursor(self):
        """
        Defines and saves a tailable cursor. While some examples of
        this strategy set the ``await_data`` option to True,
        this will block the Tornado ``ioloop``. As an experimental
        workaround, the method ``get_next()`` will schedule a brief
        timeout if there are no new results.
        """
        logging.debug("In redefine_cursor()")
        if not self.latest:
            self.latest = self._get_last()
            
        self.cursor = self.dbconn.local.oplog.rs.find(
            {"o._id": {"$gt": self.latest["o"]["_id"]}},
            sort=[("$natural", pymongo.ASCENDING),],
            tailable=True,
            await_data=False,
        )
        logging.info("Cursor reset.")
        logging.debug("--> Cursor details: %s" % self.cursor.__dict__)
        return self.cursor

    def get_next(self):
        """
        Gets the newest item from the database, invokes ``self.callback``,
        and reschedules itself on the Tornado ioloop for future
        invocation. If there are no items, the method schedules itself
        with a delay, to mimic the behavior of ``await_data`` option in
        the MongoDB cursor definition.
        """
        if not self.cursor.alive:
            logging.info("Cursor not alive; trying to reestablish.")
            self.redefine_cursor()
        try:
            next = self.cursor.next()
        except StopIteration, exc:
            self.ioloop_handler = ioloop.add_timeout(
                datetime.timedelta(milliseconds=500),
                self.get_next,
            )
            return
        except (pymongo.errors.AutoReconnect, 
                pymongo.errors.OperationFailure), exc:
            logging.info(
                "'%s: %s' on get_next(); will retry in two seconds." % 
                (type(exc).__name__, exc)
            )
            self.ioloop_handler = ioloop.add_timeout(
                datetime.timedelta(seconds=2),
                self.get_next,
            )
            return
            
        logging.debug("Received: %s" % next)
        self.latest = next
        
        try:
            self.callback(next)
        except Exception, exc:
            logging.exception(
                "Exception when invoking callback %(callback)s "
                "with next value %(next)s" %
                dict(
                    callback=callback,
                    next=next,
                )
            )
        self.ioloop_handler = ioloop.add_callback(self.get_next)
        
