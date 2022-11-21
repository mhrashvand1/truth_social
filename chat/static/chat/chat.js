let current_user_username;
let chat_ul = $('#chat');
let contact_ul = $('#contacts');

// window.onload = function(e){
//     msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
// }


let socket = new WebSocket(
'ws://' + window.location.host + '/chat/'
);

socket.onmessage = function(e) {
    let message = JSON.parse(e.data);

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

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

let msg_input = document.querySelector('#msg-input');
if (msg_input !== null) {
    msg_input.focus();
    msg_input.onkeydown = function(e) {
        const keyCode = e.which || e.keyCode;
    
        if (keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            document.querySelector('#msg-submit').click();
        }
    };
}

let msg_submit = document.querySelector('#msg-submit');
if (msg_submit !== null){
    msg_submit.onclick = function(e) {
        let messageInputDom = document.querySelector('#msg-input');
        let message = messageInputDom.value;
        socket.send(JSON.stringify({'type':'msg', 'text': message}));
        messageInputDom.value = '';
    };
}

let search_username = document.querySelector('#search-username');
search_username.onkeydown = function(e) {
    const keyCode = e.which || e.keyCode;
    if (keyCode === 13) {
        e.preventDefault();
        socket.send(
            JSON.stringify(
                {
                    'type':'search_username',
                    'username':search_username.value
                }
            )
        );
        search_username.value = '';
    }
}


//////// handlers

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





///// extra

let contact_li = $('aside li').click(function() {
    $(contact_li).removeClass('selected');
    $(this).addClass('selected');
    li = $(this);
});