import os
import threading
import multiprocessing
import signal
import zmq
 
import time

from logger import PlywoodLogger

from twisted.internet import reactor
 
from autobahn.twisted.websocket import listenWS

from autobahn.wamp1.protocol import WampServerFactory
from autobahn.wamp1.protocol import WampServerProtocol

 
class PlywoodWebSocketServerProtocol(WampServerProtocol):
 
    def onSessionOpen(self):
        self.registerForPubSub("plywood#", True)


class PlywoodWebSocketServer(object):
   
    @classmethod
    def execute(self):
        factory = WampServerFactory("ws://localhost:17998", debug = False, debugWamp = False)
        factory.protocol = PlywoodWebSocketServerProtocol
        factory.setProtocolOptions(allowHixie76 = True)

        listenWS(factory)

        reactor.run(installSignalHandlers=0) 


class PlywoodServer(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodServer, self).__init__()

        self.logging_socket = None

        self._stop = multiprocessing.Event()
        self._reactor_thread = None

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.logging_socket = self.create_logging_socket()
        self.log("Plywood WebSocket Server started on port 17998...", style="success")

        self._reactor_thread = threading.Thread(target=PlywoodWebSocketServer.execute, args=())
        self._reactor_thread.daemon = True
        self._reactor_thread.start()

        while not self._stop.is_set():
            time.sleep(1)

        reactor.callFromThread(reactor.stop)
        self._reactor_thread.join()

        self.log("Plywood WebSocket Server exited gracefully!", style="success")

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
        return "PlywoodWebSocketServer-%s" % os.getpid()
