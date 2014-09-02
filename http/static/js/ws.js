function WebSocketClient() {
    this.client = null;
    this.handlerMap = {
        open: [$.proxy(this.onOpen, this)],
        message: [$.proxy(this.onMessage, this)],
        close: [$.proxy(this.onClose, this)]
    };
}

WebSocketClient.prototype.connect = function () {
    var i,
        typeHandlers,
        type
    ;

    if (this.client !== null) {
        return;
    }

    this.client = new WebSocket("ws://" + window.location.hostname + ":8080/relay");


    for (type in this.handlerMap) {
        if (type[0] === '_') {
            continue;
        }

        handlers = this.handlerMap[type];

        for (i in handlers) {
            this.assignHandler(type, handlers[i]);
        }
    }
};

WebSocketClient.prototype.on = function (eventType, eventHandler) {
    if (this.client !== null && eventType.chatAt(0) === '_') {
        this.assignHandler(eventType, eventHandler);

        return;
    }

    if (this.handlerMap[eventType] === undefined) {
        this.handlerMap[eventType] = [];
    }

    this.handlerMap[eventType].push(eventHandler);
};

WebSocketClient.prototype.assignHandler = function (eventType, eventHandler) {
    this.client.addEventListener(eventType, eventHandler);
};

WebSocketClient.prototype.send = function (message) {
    this.client.send(JSON.stringify(message));
};

WebSocketClient.prototype.onMessage = function (event) {
    var data = JSON.parse(event.data),
        type,
        handlers,
        i
    ;

    type = '_' + data.type;

    handlers = this.handlerMap[type];

    console.log(data);

    for (i in handlers) {
        handlers[i](data.content);
    }
};

WebSocketClient.prototype.onOpen  = function (event) {};
WebSocketClient.prototype.onClose = function (event) {};