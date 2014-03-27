from server import *

import time


__version__ = "0.1b"


class PlywoodException(BaseException):
    pass


class Plywood(object):

    def __init__(self):
        self.server = None

    def run(self):
        try:
            print "################################################################################"
            print "###   Plywood STARTED!                                                       ###"
            print "################################################################################\n"

            # Start the Plywood WebSocket Server as a Process
            self.server = PlywoodServer()
            self.server.start()

            while True:
                print "MAIN"
                time.sleep(1)


        except (SystemExit, KeyboardInterrupt):
            print ""
            print "################################################################################"
            print "###   Plywood STOPPING!                                                      ###"
            print "################################################################################\n"

            self.server.shutdown()
            time.sleep(5)
