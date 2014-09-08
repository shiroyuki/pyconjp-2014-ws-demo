""" Web Socket """
import json
import threading

from pika.connection   import URLParameters
from tornado.ioloop    import IOLoop
from tornado.web       import Application
from tornado.websocket import WebSocketHandler

from amqp import AMQPManager

class MessageRelayWebSocket(WebSocketHandler):
    buddies = {}

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)

        self.id = None
        self.ip = None
        self.consumer = None

    # To override the origin check
    def check_origin(self, origin):
        return True

    def open(self):
        # At this stage, we only register this instance of websocket to the global map via the on_message method.
        self.ip = self.request.remote_ip

    def on_message(self, message):
        # All communications will be in JSON.
        data = json.loads(message)
        method_name = '_' + data['method']
        self.__getattribute__(method_name)(data)

    def on_close(self):
        # At this stage, we only unregister this instance of websocket to the global map.
        if self.id in MessageRelayWebSocket.buddies:
            del MessageRelayWebSocket.buddies[self.id]

            print('! from {} ({}, leaving)'.format(self.ip, self.id))

            self.consumer.abort()

            self.broadcast('user_leave', {'id': self.id})

            # Debug only
            print('X from {} ({})'.format(self.ip, self.id))

            return

        # Debug only
        print('X from {} (<< unknown >>)'.format(self.ip))

    def _identify(self, data):
        result = {'success': False, 'reason': None, 'id': None}
        method = data['method']
        id = data['id']

        if id in MessageRelayWebSocket.buddies:
            result['reason'] = 'Duplicated username. Try again.';

            # Debug only
            print('! from {} (<< duplicated >>)'.format(self.ip))
        else:
            # Send the buddy list
            self.send('buddy_list', {'buddies': MessageRelayWebSocket.buddies.keys()})

            # Register the current connection to the global map.
            self.id = id
            MessageRelayWebSocket.buddies[id] = self
            result['success'] = True
            result['id'] = id

            # Broadcast the entrace
            self.broadcast('user_enter', {'id': self.id})

            # Start the concurrent consumer.
            amqp = self.settings['amqp']

            def handler(channel, method, properties, body):
                data = json.loads(body)
                self.send(data['type'], data['content'])

            self.consumer = amqp.consumer('chatagent-{}'.format(self.id))
            self.consumer.consume(handler)

            # Debug only
            print('O from {} ({})'.format(self.ip, self.id))

        self.send(method, result)

    def _message(self, data):
        self.broadcast('buzz', {'sender': self.id, 'content': data['content']})

    def broadcast(self, kind, content):
        """ Send the JSON response to other clients """
        # Prepare the response
        response = {
            'type':    kind,
            'content': content
        }

        encoded_response = json.dumps(response)

        # Publish the message
        amqp = self.settings['amqp']
        publisher = amqp.publisher()
        publisher.publish(encoded_response)

    def send(self, kind, content):
        """ Send the JSON response to the client """
        response = {
            'type':    kind,
            'content': content
        }

        encoded_response = json.dumps(response)

        self.write_message(response)

def main():
    debug  = True
    routes = [
        (r'/relay', MessageRelayWebSocket),
    ]

    # Global AMQP manager
    amqp_url = URLParameters('amqp://guest:guest@localhost:5672/%2f?heartbeat_interval=15')
    amqp = AMQPManager(amqp_url)

    # Declare the exchange
    channel = amqp.channel()
    channel.exchange_declare(
        exchange = 'demo-chat',
        exchange_type = 'fanout',
        durable = True
    )
    channel.close()

    app = Application(routes, debug = debug, amqp = amqp)
    app.listen(8080, '0.0.0.0') # listen to everyone

    try:
        print('Control+C to stop the service.')
        IOLoop.instance().start()
    except KeyboardInterrupt as exception:
        print('')
        print('Gracefully shutting down the service...')

    # Ensure that all channels are closed gracefully.
    amqp.terminate()

    # Kill all running threads.
    for thread in threading.enumerate():
        if not thread.isAlive():
            continue

        thread_name = str(thread.getName())

        if thread_name == 'MainThread': continue

        try:
            thread._Thread__stop()
            print('Thread {} stopped'.format(thread_name))
        except Exception as e:
            print('Thread {} cannot be stopped. ({})'.format(thread_name, e.message))

    print('The service is now offline.')

if __name__ == '__main__':
    main()