""" Web Scoket

    This is for demonstration at PyCon JP 2014 which only work with the chat app (http://uiserver/demo/chat).

    For the real implementation
"""
from tornado.web import Application
from tornado.websocket import WebSocketHandler

class MessageRelayWebSocket(WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"

app = Application([
    (r'/ws', MessageRelayWebSocket),
])

http_server = httpserver.HTTPServer(application)
http_server.listen(8080)
ioloop.IOLoop.instance().start()