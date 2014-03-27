import sys
import threading
import multiprocessing
import signal
 
import time

from twisted.python import log
from twisted.internet import reactor
 
from autobahn.twisted.websocket import listenWS

from autobahn.wamp1.protocol import exportRpc
from autobahn.wamp1.protocol import WampServerFactory
from autobahn.wamp1.protocol import WampServerProtocol

 
class PlywoodWebSocketServerProtocol(WampServerProtocol):
 
   def onSessionOpen(self):
      self.registerForRpc(self)
      self.registerForPubSub("plywood#", True)

   @exportRpc("updateAvailableLogs")
   def update_available_logs(self):
      pass


class PlywoodWebSocketServer(object):
   
   @classmethod
   def execute(self):
      log.startLogging(sys.stdout)

      factory = WampServerFactory("ws://localhost:8998", debug = False, debugWamp = False)
      factory.protocol = PlywoodWebSocketServerProtocol
      factory.setProtocolOptions(allowHixie76 = True)

      listenWS(factory)

      reactor.run(installSignalHandlers=0) 


class PlywoodServer(multiprocessing.Process):

    def __init__(self, **params):
        super(PlywoodServer, self).__init__()

        self._stop = multiprocessing.Event()
        self._reactor_thread = None

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        print "PLYWOOD SERVER HAS STARTED!"

        self._reactor_thread = threading.Thread(target=PlywoodWebSocketServer.execute, args=())
        self._reactor_thread.daemon = True
        self._reactor_thread.start()

        while not self._stop.is_set():
            print "Plywood!"
            time.sleep(1)

        print "SUP"

        reactor.callFromThread(reactor.stop)
        self._reactor_thread.join()

        print "PLYWOOD SERVER HAS EXITED GRACEFULLY!"

    def shutdown(self):
        self._stop.set()