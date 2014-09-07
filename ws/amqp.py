import logging
from pika.adapters.blocking_connection import BlockingConnection
from pika.spec import BasicProperties
from pika.exceptions import ProbableAuthenticationError, ConsumerCancelled, ConnectionClosed
from threading import Thread, Lock

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logger = logging.getLogger(__name__)

class Message(object):
    def __init__(self, sender, body):
        self.sender = sender
        self.body   = body

class AMQPAgent(Thread):
    def __init__(self, channel):
        logger.info('Prepare')
        super(AMQPAgent, self).__init__()

        self._exchange      = 'demo-chat' # "demo-chat" exchange, durable, fan-out on all routes
        self._channel       = channel
        self._queue_name    = None
        self._queue_options = {}
        self._kwargs        = {}
        self._lock          = Lock()
        self._active        = True

    def set_queue_name(self, queue_name):
        self._queue_name = queue_name

    def set_options(self, options):
        self._queue_options = options

    @property
    def lock(self):
        return self._lock

class Publisher(AMQPAgent):
    """ Publisher

        Designed to be asynchronous and used only once.
    """
    def publish(self, message):
        self._kwargs.update({
            'exchange':    self._exchange, # force to use the fanout exchange in this demo.
            'routing_key': '',             # rounting key, but we don't need this one as we go with the exchange.
            'body':        message,        # the message body
            'properties':  BasicProperties(
                content_type  = 'application/json',
                delivery_mode = 1
            ) # force to send the message in JSON
        })

        logger.info('Publish({})'.format(self._kwargs))

        self.start()

    def run(self):
        if not self._channel.is_open:
            self._channel.open()

        self._channel.basic_publish(**self._kwargs)

class Consumer(AMQPAgent):
    """ Consumer

        Designed to concurrently constantly consume messages from the queue.
    """
    def consume(self, callback):
        if not self._queue_name:
            raise RuntimeError('Queue is not defined.')

        self._kwargs = {
            'queue':             self._queue_name,
            'consumer_callback': callback,
            'no_ack':            True # go with the auto acknowledge
        }

        self.start()

    def abort(self):
        try:
            self._channel.stop_consuming() # Stop consuming

            if not self._channel.is_open:
                self._channel.open()

            self._channel.queue_delete(self._queue_name) # Ensure that the queue is deleted.
            self._channel.close()
            print('AMQP/Consumer - Consumer {} aborted'.format(self._queue_name))
        except RuntimeError as e:
            print('AMQP/Consumer - Consumer {} aborted with error'.format(self._queue_name))
            print('AMQP/Consumer - {}: {}'.format(e.__class__.__name__, e.message))

        self._active = False

    def run(self):
        ch = self._channel

        try:
            ch.queue_declare(self._queue_name, auto_delete = True, **self._queue_options)
        except RuntimeError as e:
            ch.queue_declare(self._queue_name, passive = True, auto_delete = True, **self._queue_options)

        ch.queue_bind(queue = self._queue_name, exchange = self._exchange)
        ch.basic_consume(**self._kwargs)

        try:
            ch.start_consuming()
        except ConsumerCancelled as e:
            print('AMQP/Consumer - Consumer {} cancelled'.format(self._queue_name))
        except ConnectionClosed as e:
            print('AMQP/Consumer - Connection {} closed'.format(self._queue_name))

class AMQPManager(object):
    """ AMQP Manager

        This is used to keep tracking on concurrent connections such that the
        cleanup procedure can gracefully terminate the connections.
    """
    def __init__(self, parameters):
        self._parameters      = parameters
        self._connection_type = BlockingConnection
        self._connection      = None
        self._agent           = {}

    def connection(self):

        if not self._connection:
            self._connection = self._connection_type(self._parameters)

        return self._connection

    def channel(self):
        return self.connection().channel()

    def publisher(self):
        channel = self.channel()

        return Publisher(channel)

    def consumer(self, id):
        if id in self._agent and self._agent[id]._active:
            return self._agent[id]

        print('AMQP - create consumer for {}'.format(id))

        # "id" is also a queue name.
        channel  = self.channel()
        consumer = Consumer(channel)
        consumer.set_queue_name(id)

        self._agent[id] = consumer

        return consumer

    def terminate(self):
        for id in self._agent:
            if id in self._agent:
                consumer = self._agent[id]
                consumer.abort()
