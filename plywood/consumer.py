import os
import threading
import multiprocessing
import zmq
import signal

from logger import *
from client import *


class PlywoodConsumer(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodConsumer, self).__init__()
        self._stop = multiprocessing.Event()

        self.web_socket_client = None
        self.logging_socket = None

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.logging_socket = self.create_logging_socket()
        self.web_socket_client = PlywoodClient()

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

    def _origin(self):
        return "%s-%s" % (self.__class__.__name__, os.getpid())
