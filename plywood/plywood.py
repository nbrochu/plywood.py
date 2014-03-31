import os
import zmq
import logging

from logger import *
from consumer_pool import *
from server import *


class PlywoodException(BaseException):
    pass


class Plywood(object):

    def __init__(self, **params):
        self._zmq_context = zmq.Context()

        self.socket = self._zmq_context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:17990")

        logging.basicConfig(level=logging.DEBUG, format="")
        self.logger = logging.getLogger("plywood")

        self.plywood_logger = None
        self.plywood_consumer_pool = None
        self.plywood_server = None

    def run(self):
        try:
            # Start the Plywood Logger as a Process
            self.plywood_logger = PlywoodLogger()

            started_message = PlywoodLogger.prepare_log("Plywood STARTED!", "Plywood-%s" % os.getpid(), "success")
            self.logger.info(self.plywood_logger.wrap_message(started_message))

            self.plywood_logger.start()

            # Start the Plywood Consumer Pool as a Process
            self.plywood_consumer_pool = PlywoodConsumerPool.initialize(consumer_type="redis")
            self.plywood_consumer_pool.start()

            # Start the Plywood WebSocket Server as a Process
            self.plywood_server = PlywoodServer()
            self.plywood_server.start()

            # Log Printing Loop
            while True:
                message = self.socket.recv()
                self.logger.debug(message)

                self.socket.send("ACK")


        except (SystemExit, KeyboardInterrupt):
            stopping_message = PlywoodLogger.prepare_log("Plywood STOPPING...", "Plywood-%s" % os.getpid(), "success")
            self.logger.info(self.plywood_logger.wrap_message(stopping_message))

            self.plywood_consumer_pool.shutdown()
            self.plywood_server.shutdown()

            # Listen for messages for up to 10 seconds before shutting down the logger
            # Not doing this would block a process trying to log a message while attempting a graceful exit

            poller = zmq.Poller()
            poller.register(self.socket, zmq.POLLIN)

            for i in xrange(20):
                poll_result = poller.poll(500)

                if len(poll_result) > 0:
                    message = self.socket.recv()
                    self.logger.debug(message)

                    self.socket.send("ACK")

            self.plywood_logger.shutdown()
