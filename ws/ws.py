""" Web Scoket

    This is for demonstration at PyCon JP 2014 which only work with the chat app (http://uiserver/demo/chat).

    For the real implementation
"""
from tornado.ioloop    import IOLoop
from tornado.web       import Application
from tornado.websocket import WebSocketHandler

class MessageRelayWebSocket(WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"

def main():
    debug  = True
    routes = [
        (r'/ws', MessageRelayWebSocket),
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