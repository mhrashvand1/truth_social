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
//////////////////////////////////////////////////////////////////
/////////////////////////// handlers /////////////////////////////
//////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////

function chatMessageHandler(message){
    let li_class = 'you';
    if (message['sender_username'] === current_user_username){
        li_class = 'me';
    } 
    addMessageLI(
        {
            li_class:li_class,
            sender_username:message['sender_username'],
            sender_name:message['sender_name'],
            datetime:message['datetime'],
            text:message['text'],
            prepend_or_append:'append'
        }
    );
    chat_ul.scrollTop(chat_ul.prop("scrollHeight"));
    // ... scroll (fix or down), last_read, ...(اینو با رویداد خود اسکرول قاطی نکن.)
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
        contactRemoveSelected();
        if (search_username.value.toLowerCase() === current_user_username){
            truthSocialBotMessage({
                message:`${search_username.value} is your username baby.`,
                code: ''
            });
            search_username.value = '';
            return;
        }
        let contact = document.querySelector(`aside li[data-username=${search_username.value}]`);
        if (contact !== null){
            contact.click();
        }
        else {
            socket.send(JSON.stringify({'type':'search_username','username':search_username.value}));
        }
        search_username.value = '';
    }
}

function contactClickHandler(e){
    let target = e.target;
    if (target.tagName !== 'LI'){
        target = target.parentElement.closest('li');
    }
    contactRemoveSelected();
    contactAddSelected(target);
    addMainFooter(); 
    addMainHeader({
        'avatar':target.querySelector('img').getAttribute('src'),
        'username':target.getAttribute('data-username'),
        'roomid':target.getAttribute('data-roomid'),
        'name':target.querySelector('.contact-name-aside').innerText,
        'online_status':''
    });
    // online status, ...  get online status by send request to server
    cleanChatUL(); // temporary  it will complete in load messages
    // load messages -> delete old one, ...
}

function searchUsernameMessageHandler(message){
    console.log(message);
    if (message['status'] === 404){
        truthSocialBotMessage({
            message:`user with username ${message['username']} not found.`,
            code: 404
        });
    }
    else{
        cleanChatUL();
        addMainFooter();
        addMainHeader(message);
        // وصل شدن به روم جدید در صورت ارسال اولین پیام؟ خب این مال اینجا نیست.
        // بعد از تشکیل روم و اضافه شدن کانتکت و فراخانی اد سلکت وصل میشه به روم جدید.
        // البته وقتی روم تشکیل شد و به کانتکتا اضافه شد کافیه کلیک رو فرا بخونیم  خودش بقیه کارا رو انجام میدع
        // حواست باشه کلیک رو فقط برای شخصی که اولین مسیج رو فرستاده باید بزنیم!!
        // ینی توی جوابی که سرور میفرسته و تایپش مقلا کریت نیو روم هست یه متغییر داره به نام هو کریت روم و اگه برابر با تو بود اونوقت کلیک میشه رو کانتکت
    }
}

///////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////
/////////////////////////// utils /////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////

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
    <textarea id="msg-input" placeholder="Type your message" maxlength="1000" onkeydown="msgInputKeydownHandler(event)"></textarea>
    <button id="msg-submit" type="submit" onclick="msgSubmitOnclickHandler(event)">Send</button> 
    `;  
    document.querySelector('#msg-input').focus();
}

function contactRemoveSelected(){
    let contact = document.querySelector(`aside li.selected`);
    if (contact !== null){
        contact.classList.remove('selected');
        // TODO disconnect to room (send disconnect request to server)
    }
}
function contactAddSelected(aside_li_tag){
    // TODO connect to room
    aside_li_tag.classList.add('selected');
}

function addMainHeader(data){
    let main_header = document.querySelector('#main-header');
    main_header.innerHTML = `
    <img src="${data['avatar']}" alt="" width="50" height="50">
    <div data-username="${data['username']}" data-roomid="${data['roomid']}">
        <h2 class="contact-name-main">${data['name']}</h2>
        <h3 class="online-status">${data['online_status']}</h3>
    </div>
    `;
}

function loadMessages(){
    return;
}

function truthSocialBotMessage({message='', code=''}={}){
    // cleanMainHeader();
    cleanChatUL();
    cleanMainFooter();
    addMainHeader({
        'avatar':'http://'+window.location.host+'/media/truth_social_media/truth_social_bot.png',
        'name':'truth social',
        'online_status':'always online'
    });
    let currentdate = new Date(); 
    let datetime =  currentdate.getDate() + "/"
                    + (currentdate.getMonth()+1)  + "/" 
                    + currentdate.getFullYear() + " @ "  
                    + currentdate.getHours() + ":"  
                    + currentdate.getMinutes() + ":" 
                    + currentdate.getSeconds();
    let text = `${message} ${code}`;
    addMessageLI({
        li_class:'you',
        sender_name:'truth social', 
        datetime:datetime,
        text:text
    });

}

function addMessageLI({
    li_class='you', datetime='', sender_name='', 
    sender_username='', text='', prepend_or_append='append'
}={})
{
    let color = 'green';
    if (li_class === 'me'){
        color = 'blue';
    }
    
    let li = `
    <li class="LICLASS" data-username="SENDERUSERNAME">
        <div class="entete">
            <h3>DATETIME</h3>
            <h2>SENDERNAME</h2>
            <span class="status COLOR"></span>
        </div>
        <div class="triangle"></div>
        <div class="message">
            MESSAGETEXT
        </div>
    </li>
    `.replace('LICLASS', li_class).replace('SENDERUSERNAME', sender_username
    ).replace('DATETIME', datetime).replace('SENDERNAME', sender_name
    ).replace('COLOR', color).replace('MESSAGETEXT', text)

    if (prepend_or_append === 'append'){
        chat_ul.append(li);
    }
    else{
        chat_ul.prepend(li);
    }
     
}

/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////
//////////////////////////// extra //////////////////////////////
/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

// let contact_li = $('aside li').click(function() {
//     $(contact_li).removeClass('selected');
//     $(this).addClass('selected');
//     li = $(this);
// });

