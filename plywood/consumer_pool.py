import os
import multiprocessing
import zmq
import signal

from logger import *


class PlywoodConsumerPool(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodConsumerPool, self).__init__()
        self._stop = multiprocessing.Event()

        self.pool_size = params.get("pool_size") or 4
        self.consumers = None

        self.logging_socket = None

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.logging_socket = self.create_logging_socket()

    def shutdown(self):
        self._stop.set()

    def log(self, message, style="normal"):
        prepared_message = PlywoodLogger.prepare_log(message, self._origin(), style)

        self.logging_socket.send_unicode(prepared_message)
        self.logging_socket.recv()

    def create_logging_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:17991")

        return socket

    def _initialize_consumers(self):
        pass  # Implement in child classes

    def _origin(self):
        return "%s-%s" % (self.__class__.__name__, os.getpid())

    @classmethod
    def initialize(self, consumer_type="redis", pool_size=4):
        from consumer_pools import *

        consumer_pool_class_mappings = {
            "redis": PlywoodRedisConsumerPool
        }

        return consumer_pool_class_mappings[consumer_type](pool_size=pool_size)
