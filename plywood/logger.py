import os
import signal
import multiprocessing
import zmq

from datetime import datetime


class PlywoodLogger(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodLogger, self).__init__()

        self.socket = None

        self._pid = os.getppid()
        self._stop = multiprocessing.Event()

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.create_server_socket()
        client_socket = self.create_client_socket()

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        self.log("Plywood Logger started!", "success")

        while not self._stop.is_set():
            poll_result = poller.poll(1000)

            if len(poll_result) > 0:
                message = self.socket.recv()
                wrapped_message = self.wrap_message(unicode(message, "UTF-8"))

                client_socket.send_unicode(wrapped_message)
                client_socket.recv()

                self.socket.send("ACK")

    def shutdown(self):
        self._stop.set()

    def create_server_socket(self):
        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:17991")

    def create_client_socket(self):
        socket = zmq.Context().socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:17990")

        return socket

    def wrap_message(self, message):
        return u"[%s][%s] %s" % (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), message.split("|||")[1], message.split("|||")[0])

    def log(self, message, style="normal"):
        prepared_message = PlywoodLogger.prepare_log(message, self._origin(), style)

        client_socket = self.create_client_socket()

        client_socket.send_unicode(self.wrap_message(prepared_message))
        client_socket.recv()

    def _origin(self):
        return "PlywoodLogger-%s" % os.getpid()

    @classmethod
    def prepare_log(self, message, origin="GENERAL", style="normal"):
        style_lambdas = {
            "normal": lambda m: message,
            "success": lambda m: "\033[92m" + message + "\033[0m",
            "warning": lambda m: "\033[93m" + message + "\033[0m",
            "error": lambda m: "\033[91m" + message + "\033[0m"
        }

        return (style_lambdas[style](message) + "|||" + origin)
