""" Web Socket """
import json
from tornado.ioloop    import IOLoop
from tornado.web       import Application
from tornado.websocket import WebSocketHandler

class MessageRelayWebSocket(WebSocketHandler):
    buddies = {}

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)

        self.id = None
        self.ip = None

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

            # Debug only
            print('O from {} ({})'.format(self.ip, self.id))

        self.send(method, result)
    
    def _message(self, data):
        self.broadcast('buzz', {'sender': self.id, 'content': data['content']})

    def broadcast(self, kind, content):
        """ Send the JSON response to other clients """
        for id in MessageRelayWebSocket.buddies:
            buddy = MessageRelayWebSocket.buddies[id]

            if self.id == buddy.id:
                continue

            buddy.send(kind, content)

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

    app = Application(routes, debug = debug)
    app.listen(8080, '0.0.0.0') # listen to everyone

    try:
        print('Control+C to stop the service.')
        IOLoop.instance().start()
    except KeyboardInterrupt as exception:
        print('')
        print('Gracefully shutting down the service...')

    print('The service is now offline.')

if __name__ == '__main__':
    main()