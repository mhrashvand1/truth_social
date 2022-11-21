var current_user_username;
var chat_ul = $('#chat');
var contact_ul = $('#contacts');

// window.onload = function(e){
//     msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
// }


var socket = new WebSocket(
'ws://' + window.location.host + '/chat/'
);

socket.onmessage = function(e) {
    var message = JSON.parse(e.data);

    switch (message['type']) {
        case "get_current_user_data":
            current_user_username = message['username']
            break;
        case "user_not_authenticated":
            window.location.replace(
                'http://' + window.location.host + '/chat/login/'
            );
            break;
        case "msg":
            messageHandler(message);
            chat_ul.scrollTop(chat_ul.prop("scrollHeight"));
            break;
        default:
            break;
    }
};

function messageHandler(message){
    chat_ul.append(`
        <li class="me">
            <div class="entete">
                <h3>DATETIME</h3>
                <h2>SENDERNAME</h2>
                <span class="status blue"></span>
            </div>
            <div class="triangle"></div>
            <div class="message">
                MESSAGETEXT
            </div>
        </li>
        `.replace(
            'DATETIME', message['datetime']
        ).replace(
            'SENDERNAME', current_user_username
        ).replace(
            'MESSAGETEXT', message['text']
        )
    );
}


socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

document.querySelector('#msg-input').focus();
document.querySelector('#msg-input').onkeydown = function(e) {
    const keyCode = e.which || e.keyCode;

    if (keyCode === 13 && !e.shiftKey) {
        e.preventDefault();
        document.querySelector('#msg-submit').click();
    }
};

document.querySelector('#msg-submit').onclick = function(e) {
    var messageInputDom = document.querySelector('#msg-input');
    var message = messageInputDom.value;
    socket.send(JSON.stringify({'text': message, 'sender':current_user_username}));
    messageInputDom.value = '';
};


var contact_li = $('aside li').click(function() {
    $(contact_li).removeClass('selected');
    $(this).addClass('selected');
    li = $(this);
});