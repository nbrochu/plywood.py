import threading

from twisted.internet import reactor
 
from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory
from autobahn.wamp1.protocol import WampClientProtocol

 
class PlywoodWebSocketClientProtocol(WampClientProtocol):

   def done(self):
      self.sendClose()
      reactor.stop()
 
   def onSessionOpen(self):
      self.factory.protocol_instance = self
      self.factory.base_client.connected_event.set()

   def publish_plywood_event(self, plywood_event):
      self.publish("plywood#plywood", plywood_event)


class PlywoodWebSocketClientFactory(WampClientFactory):

   def __init__(self, *args, **kwargs):
      WampClientFactory.__init__(self, *args, **kwargs)

      self.protocol_instance = None
      self.base_client = None


class PlywoodClient(object):

   def __init__(self):
      self.factory = None
      self.connected_event = threading.Event()
      self.reactor_thread = None

   def connect(self):
      self.factory = PlywoodWebSocketClientFactory("ws://0.0.0.0:17998", debug = False, debugWamp = False)
      self.factory.protocol = PlywoodWebSocketClientProtocol
      self.factory.base_client = self

      connectWS(self.factory)

      self.reactor_thread = threading.Thread(target=reactor.run, args=(False,))
      self.reactor_thread.daemon = True
      self.reactor_thread.start()

   def close(self):
      reactor.callFromThread(reactor.stop)
      self.reactor_thread.join()

   @property
   def connected(self):
      return False if not self.connected_event.wait(timeout=5) else True

   def publish(self, plywood_event):
      if self.connected == False:
         self.close()

      reactor.callFromThread(self.factory.protocol_instance.publish_plywood_event, plywood_event)
