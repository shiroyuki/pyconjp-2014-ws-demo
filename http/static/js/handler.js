function onEnterPress(e) {
    if (e.keyCode === 13) {
        e.preventDefault();
        selectors.newMessageForm.trigger('submit');
    }
}

function onLoginSubmit(e) {
    var $form  = $(this),
        $input = $form.find('[name=sname]'),
        content = $.trim($input.val())
    ;

    e.preventDefault();

    if (content.length === 0) {
        return;
    }

    selectors.allInputs.attr('disabled', true);

    websocket.send({
        method: 'identify',
        id: content
    });
}

function onNewMessageSubmit(e) {
    var $form  = $(this),
        $input = $form.find('[name=message]'),
        content = $.trim($input.val())
    ;

    e.preventDefault();

    if (content.length === 0) {
        return;
    }

    $input.val('');

    websocket.send({
        method: 'message',
        content: content
    });
    
    renderMessage(id, content);
}

function onWSOpen(event) {
    selectors.allInputs.attr('disabled', false);
    selectors.reconnection.hide();
}

function onWSClose(event) {
    selectors.reconnection.show();
    selectors.body.addClass('offline');
    console.log('WS disconnected');
}

function onWSIdentify(data) {
    selectors.allInputs.attr('disabled', false);
    
    if (!data.success) {
        alert(data.reason);
        
        return;
    }
    
    id = data.id
    
    renderAttendee(data.id);
    selectors.body.removeClass('overlay-enabled');
    selectors.loginForm.hide();
}

function onWSUserEnter(data) {
    renderAttendee(data.id);
}

function onWSUserLeave(data) {
    selectors.attendees.find('.attendee[data-id=' + data.id + ']').remove();
}

function onWSBuddyList(data) {
    for (i in data.buddies) {
        renderAttendee(data.buddies[i]);
    }
}

function onWSBuzz(data) {
    renderMessage(data.sender, data.content);
}