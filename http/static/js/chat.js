var templates = new TemplateController(),
    selectors = {},
    websocket = new WebSocketClient()
;

function renderAttendee(alias, email) {
    var template = templates.get('attendee'),
        $template
    ;

    $template = $(template);

    $template.children('.alias').text(alias);

    if (email === undefined) {
        $template.addClass('no-email');
        $template.children('.email').remove();
    } else {
        $template.children('.email').text(email);
    }

    selectors.attendees.append($template);
}

function renderMessage(sender, content) {
    var template = templates.get('message'),
        $template
    ;

    $template = $(template);

    $template.children('.sender').text(sender);
    $template.children('.content').text(content);

    selectors.newMessageForm.after($template);
}

function main() {
    selectors.body           = $('body');
    selectors.attendees      = $('.attendees');
    selectors.conversation   = $('.conversation');
    selectors.loginForm      = $('.overlay form.login');
    selectors.newMessageForm = selectors.conversation.find('.message.new');

    selectors.loginForm.on('submit', onLoginSubmit);
    selectors.newMessageForm.on('submit', onNewMessageSubmit);
    selectors.newMessageForm.find('[name=message]').on('keypress', onEnterPress);

    websocket.connect();

    /*
    renderAttendee('Juti', 'jnopporn@shiroyuki.com');
    renderAttendee('Sean', 'sean@wine.fr');
    renderAttendee('George', 'george@maple.ca');
    renderAttendee('中山', 'nakayama@sushi.jp');
    */

    /*
    renderMessage('中山', 'こんにちはみんなさん。');
    renderMessage('George', 'Greeting!');
    renderMessage('George', '/me eating Beaver Tail');
    renderMessage('Juti', 'Eh!');
    renderMessage('Sean', 'Bonjour!');
    */
}

$(document).ready(main);