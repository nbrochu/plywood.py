import signal
import zmq
import multiprocessing
import traceback

from logger import *

class PlywoodListener(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodListener, self).__init__()

        self.socket = None
        self.logging_socket = None

        self._stop = multiprocessing.Event()

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.logging_socket = self.create_logging_socket()
        self.log("Plywood listening on port 7999...", style="success")

        self.create_server_socket()

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while not self._stop.is_set():
            poll_result = poller.poll(1000)

            if len(poll_result) > 0:
                message = self.socket.recv()

                try:
                    self.process_message(message)
                except Exception, e:
                    self.socket.send("Error: %s - %s" % (e.message, traceback.format_exc()))

        self.log("Plywood Listener exited gracefully!", style="success")

    def shutdown(self):
        self._stop.set()

    def log(self, message, style="normal"):
        prepared_message = PlywoodLogger.prepare_log(message, self._origin(), style)

        self.logging_socket.send_unicode(prepared_message)
        self.logging_socket.recv()

    def create_logging_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:7991")

        return socket

    def create_server_socket(self):
        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind("tcp://0.0.0.0:7999")

    def process_message(self, message):
        self.log(message)

    def _origin(self):
        return "PlywoodListener-%s" % os.getpid()