# HMMX Prototype

This is a prototype of HMMX and a demo used for the talk at PyCon JP 2014.

The real difference between the demo and the real one is the framework.
The demo version uses the pure combination of Flask and Tornado. However,
the real version uses Tori Framework, which is a wrapper of Tornado, to
handle both UI and websocket and integrate with the remote **voila-id**
service.
