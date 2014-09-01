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

    // TODO validate the uniqueness before proceeding beyond this point.
    //      (Only required for mentioning - Extra)

    renderAttendee(content);
    selectors.body.removeClass('overlay-enabled');
    selectors.loginForm.hide();
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

    // TODO Replace the code below with the callback from the websocket.
    renderMessage('Me', content);
}
