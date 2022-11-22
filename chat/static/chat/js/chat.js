let current_user_username;
let chat_ul = $('#chat');
let contact_ul = $('#contacts');


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
        case "chat_message":
            chatMessageHandler(message);
            break;
        case "search_username":
            searchUsernameMessageHandler(message);
            break;
        default:
            break;
    }
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};


//////////////////////////////////////////////////////////////////
/////////////////////////// handlers /////////////////////////////
//////////////////////////////////////////////////////////////////

function chatMessageHandler(message){
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
    chat_ul.scrollTop(chat_ul.prop("scrollHeight"));
    // ...
}

function msgInputKeydownHandler(e){
    const keyCode = e.which || e.keyCode;   
    if (keyCode === 13 && !e.shiftKey) {
        e.preventDefault();
        document.querySelector('#msg-submit').click();
    }
}
function msgSubmitOnclickHandler(e){
    let messageInputDom = document.querySelector('#msg-input');
    let message = messageInputDom.value;
    socket.send(JSON.stringify({'type':'chat_message', 'text': message}));
    messageInputDom.value = '';
    // ...
}

function searchUsernameSubmitHandler(e){
    let search_username = document.querySelector('#search-username');

    const keyCode = e.which || e.keyCode;
    if (keyCode === 13) {

        e.preventDefault();
        if (search_username.value.toLowerCase() === current_user_username){
            console.log(`${search_username.value} is your username.`)
            search_username.value = '';
            return;
        }
        contactRemoveSelected();

        let contact = document.querySelector(`aside li[data-username=${search_username.value}]`);

        if (contact !== null){
            contact.click();
        }
        else {
            socket.send(
                JSON.stringify(
                    {
                        'type':'search_username',
                        'username':search_username.value
                    }
                )
            );
        }
        search_username.value = '';
    }
}

function contactClickHandler(e){
    let target = e.target;
    if (target.tagName !== 'LI'){
        target = target.parentElement.closest('li');
    }
    target.classList.add('selected');
    addMainFooter(); 
    // ... add main header, load messages, online status, ...
    // load messages -> delete old one, ...
}

function searchUsernameMessageHandler(message){
    console.log(message);
    if (message['status'] === 404){
        cleanMainHeader();
        cleanChatUL();
        cleanMainFooter();
        // TODO TruthSocial bot message ('user with username ... not fount')
        //... clean main header, chats, main footer and show 404
    }
    else{
        addMainFooter();
        addMainHeader(message);
    }
}
//////////////////////////////////////////////////////////////////////
/////////////////////////// utils ////////////////////////////////////
//////////////////////////////////////////////////////////////////////

function cleanMainHeader(){
    document.querySelector('#main-header').innerHTML = '';
}

function cleanChatUL(){
    document.querySelector('#chat').innerHTML = '';
}

function cleanMainFooter(){
    document.querySelector('#main-footer').innerHTML = '';
}

function addMainFooter(){
    footer = document.querySelector('#main-footer');
    footer.innerHTML = `
    <textarea id="msg-input" placeholder="Type your message" maxlength="1000"></textarea>
    <button id="msg-submit" type="submit">Send</button> 
    `;  
    let msg_input = document.querySelector('#msg-input');
    let msg_submit = document.querySelector('#msg-submit');
    msg_input.focus();
    msg_input.onkeydown = msgInputKeydownHandler;
    msg_submit.onclick = msgSubmitOnclickHandler;
}

function contactRemoveSelected(){
    $('aside li').removeClass('selected');
}

function addMainHeader(data){
    let main_header = document.querySelector('#main-header');
    main_header.innerHTML = `
    <img src="${data['avatar']}" alt="" width="50" height="50">
    <div data-username="${data['username']}" data-roomid="">
        <h2 class="contact-name-main">${data['name']}</h2>
        <h3 class="online-status">${data['online_status']}</h3>
    </div>
    `;
}

function loadMessages(){
    return;
}
/////////////////////////////////////////////////////////////////
//////////////////////////// extra //////////////////////////////
/////////////////////////////////////////////////////////////////

let contact_li = $('aside li').click(function() {
    $(contact_li).removeClass('selected');
    $(this).addClass('selected');
    li = $(this);
});

