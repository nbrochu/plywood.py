import time
import threading
import zmq
import redis
import json

from plywood.consumer import *


class PlywoodRedisConsumer(PlywoodConsumer):

    def __init__(self, **params):
        super(PlywoodRedisConsumer, self).__init__(**params)

        self.redis = None
        self.redis_queue = self._redis_queue(**params)

        self.pool_listen_thread = None

    def run(self):
        super(PlywoodRedisConsumer, self).run()
        self.log("Starting Plywood Redis Consumer...")

        self.create_pool_listen_thread()
        self.redis = redis.StrictRedis(connection_pool=redis.ConnectionPool(host="198.245.63.41", port=6379, db=0)) # TODO: Extract to config...

        self.web_socket_client.connect()

        while not self._stop.is_set():
            event = self.redis.lpop(self.redis_queue)

            if event is None:
                time.sleep(0.25)
                continue

            try:
                parsed_event = json.loads(event)
            except Exception:
                parsed_event = None

            if parsed_event is None:
                self.log("Log Entry consumed from Redis - Backlog: %d" % self.redis.llen(self.redis_queue))
            else:
                self.log("%s: Log Entry consumed from Redis - Backlog: %d" % (parsed_event.get("type"), self.redis.llen(self.redis_queue)))

            self.web_socket_client.publish(event)

        self.log("Plywood Redis Consumer exited gracefully!")

    def create_pool_listen_thread(self):
        self.pool_listen_thread = PlywoodRedisConsumerPoolListenThread(redis_consumer = self)
        self.pool_listen_thread.setDaemon(True)

        self.pool_listen_thread.start()

    def _redis_queue(self, **params):
        return params.get("queue") or "plywood-events"


class PlywoodRedisConsumerPoolListenThread(threading.Thread):

    def __init__(self, **params):
        super(PlywoodRedisConsumerPoolListenThread, self).__init__()

        self.redis_consumer = params.get("redis_consumer")

        self.socket = zmq.Context().socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:17993")

        self.socket.setsockopt(zmq.SUBSCRIBE, "plywood-consumers")

    def run(self):
        while True:
            message = self.socket.recv()
            # Do nothing... (for now!)
