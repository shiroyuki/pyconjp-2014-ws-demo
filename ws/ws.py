""" Web Socket """
from tornado.ioloop    import IOLoop
from tornado.web       import Application
from tornado.websocket import WebSocketHandler

class MessageRelayWebSocket(WebSocketHandler):
    buddies = {}

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)

        self.id = None
        self.ip = None
        self.key = None

    # To override the origin check
    def check_origin(self, origin):
        return True

    def open(self):
        # At this stage, we only register this instance of websocket to the global map via the on_message method.
        self.ip = self.request.remote_ip

    def on_message(self, message):
        print('- {} ({}): {}'.format(self.ip, self.id, message))
        self.write_message("You said: " + message)

    def on_close(self):
        # At this stage, we only unregister this instance of websocket to the global map.
        if self.key in MessageRelayWebSocket.buddies:
            del MessageRelayWebSocket.buddies[self.key]
            print('X from {} ({})'.format(self.ip, self.id))

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