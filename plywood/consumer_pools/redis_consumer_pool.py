import time
import zmq

from plywood.consumer_pool import *
from plywood.consumers import *


class PlywoodRedisConsumerPool(PlywoodConsumerPool):

    def __init__(self, **params):
        super(PlywoodRedisConsumerPool, self).__init__(**params)

        self.socket = None

    def run(self):
        super(PlywoodRedisConsumerPool, self).run()
        self.log("Starting Plywood Redis Consumer Pool... Workers: %d" % self.pool_size, style="success")

        self.create_publisher_socket()
        self.consumers = self._initialize_consumers()

        while not self._stop.is_set():
            time.sleep(1)

        for consumer in self.consumers:
            consumer.shutdown()

        self.log("Plywood Redis Consumer Pool exited gracefully!", style="success")

    def create_publisher_socket(self):
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:17993")

    def _initialize_consumers(self):
        consumers = []

        for i in xrange(self.pool_size):
            consumer = PlywoodRedisConsumer()
            consumer.start()

            consumers.append(consumer)

        return consumers
