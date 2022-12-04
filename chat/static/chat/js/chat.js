let current_user_username;
let current_user_name;
let current_user_avatar;
let chat_ul = $('#chat');
let chat = document.getElementById("chat");
let contact_ul = $('#contacts');


let socket = new WebSocket(
'ws://' + window.location.host + '/chat/'
);

socket.onmessage = function(e) {
    let message = JSON.parse(e.data);

    switch (message['type']) {
        case "get_current_user_data":
            current_user_username = message['username'];
            current_user_name = message['name'];
            current_user_avatar = message['avatar'];
            showCurrentUserData();
            break;
        case "user_not_authenticated":
            window.location.replace(
                'http://' + window.location.host + '/chat/login/'
            );
            break;
        case "load_contacts":
            loadContactsMessageHandler(message); //// why?  why slash?
            break;
        case "chat_message":
            chatMessageHandler(message);
            break;
        case "search_username":
            searchUsernameMessageHandler(message);
            break;
        case "you_are_blocked":
            showBlockMessageHandler(message);
            break;
        case "add_contact":
            addContactMessageHandler(message);
            break;
        case "delete_contact":
            deleteContactMessageHandler(message);
            break;
        case "load_messages":
            loadMessagesMessageHandler(message);
            break;
        case "notification":
            notificationMessageHandler(message);
            break;
        case "online_status":
            break;
        default:
            break;
    }
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// socket message handlers /////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function loadContactsMessageHandler(message){
    let contacts = message['results'];
    for (let i=0; i<contacts.length; i++){
        addContactLI({
            username:contacts[i]['username'],
            name:contacts[i]['name'],
            avatar:contacts[i]['avatar'],
            roomid:contacts[i]['room_id'],
            new_msg_count:contacts[i]['new_msg_count'],
            last_msg_time:contacts[i]['last_message_time']
        });
    }
}

function addContactMessageHandler(message){
    addContactLI({
        username:message['username'],
        name:message['name'],
        avatar:message['avatar'],
        roomid:message['room_id'],
        new_msg_count:message['new_msg_count'],
        last_msg_time:message['last_message_time'],
        prepend_or_append:"prepend"
    });
    if (message['actor']===current_user_username){
        let contact = document.querySelector(`aside li[data-username=${message['username']}]`);
        if (contact !== null){
            contact.click();
        }
    }
}

function deleteContactMessageHandler(message){
    let username = message['username']
    let contact = document.querySelector(`aside li[data-username=${username}]`);
    if (contact !== null){
        if (contact.classList.contains("selected")){
            contactRemoveSelected();
            cleanMainHeader();
            cleanChatUL();
            cleanMainFooter();
        }
        document.querySelector("#contacts").removeChild(contact);
    }
}

let isLoadingMessages = false;

function loadMessagesMessageHandler(message){
    isLoadingMessages = true;
    let initial = message['initial'];
    let messages = message['results'];
    
    if (! messages.length > 0){
        return;
    }
    if ((! initial)){
        document.getElementById("chat").scrollBy({
            top:chat.scrollTop + 1, 
        }); 
    }

    for (let i=0; i<messages.length; i++){
        let li_class = 'you';
        if (messages[i]['sender_username'] === current_user_username){
            li_class = 'me';
        }
        addMessageLI({
            li_class:li_class,
            sender_username:messages[i]['sender_username'],
            sender_name:messages[i]['sender_name'],
            datetime:messages[i]['datetime'],
            text:messages[i]['text'],
            message_id:messages[i]['message_id'],
            prepend_or_append:'prepend'
        });
    }
    
    if (initial){
        if (! chatIsScrollable()){
            console.log("is not scrollable.(1)");
        }
        else{
            scrollDownIsHandling = false;
            document.getElementById("chat").scrollBy({
                top:chat_ul.prop("scrollHeight"), 
                behavior:"smooth"
            });
        }
    }
    isLoadingMessages = false;
    scrollUpIsHandling = false;
}

function chatMessageHandler(message){
    let li_class = 'you';
    if (message['sender_username'] === current_user_username){
        li_class = 'me';
    } 
    let scrollBottom = getChatScrollBottom();
    addMessageLI({
        li_class:li_class,
        sender_username:message['sender_username'],
        sender_name:message['sender_name'],
        datetime:message['datetime'],
        text:message['text'],
        message_id:message['message_id'],
        prepend_or_append:'append'
    });
    if(li_class === 'me' || scrollBottom < 2){
        if (! chatIsScrollable()){
            console.log("is not scrollable.(2)");
        }
        else{
            scrollDownIsHandling = false;
            document.getElementById("chat").scrollBy({
                top:chat_ul.prop("scrollHeight"), 
                behavior:"smooth"
            });
        }
    }
}

function notificationMessageHandler(message){

}

function onlineStatusMessageHandler(message){

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
    }
}

function showBlockMessageHandler(message){
    let blocker_username = message['blocker'];
    truthSocialBotMessage({
        message:`${blocker_username} has blocked you :((`,
        code: '403'
    });
}
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// event handlers /////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function msgInputKeydownHandler(e){
    const keyCode = e.which || e.keyCode;   
    if (keyCode === 13 && !e.shiftKey) {
        e.preventDefault();
        document.querySelector('#msg-submit').click();
    }
}
function msgSubmitClickHandler(e){
    let messageInputDom = document.querySelector('#msg-input');
    let message = messageInputDom.value;
    if (message.length === 0){
        return;
    }
    let username = $("#main-header div").attr('data-username');
    socket.send(JSON.stringify({'type':'chat_message', 'text': message, 'to':username}));
    messageInputDom.value = '';

    selected_contact = document.querySelector("aside li.selected");
    if (selected_contact !== null){
        let currentdate = new Date();
        let datetime = standardDateTimeFormat(currentdate);
        updateLastMsgTime({target:selected_contact, datetime:datetime});
    }
}

function searchUsernameKeydownHandler(e){
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
    if (target.classList.contains("contact-delete-icon")){
        return;
    }
    let li_target = target;
    if (li_target.tagName !== 'LI'){
        li_target = li_target.parentElement.closest('li');
    }
    if (checkClickOnNewContact(li_target) === false){
        return;
    }
    contactRemoveSelected();
    contactAddSelected(li_target);
}

function contactDBClickHandler(e){
    if (! chatIsScrollable()){
        console.log("is not scrollable.(3)");
    }
    else{
        scrollDownIsHandling = false;
        document.getElementById("chat").scrollBy({
            top:chat_ul.prop("scrollHeight"), 
            behavior:"smooth"
        });
    }
}

function deleteContactRequestHandler(e){
    let target = e.target;
    let li = target.parentElement.closest('li');
    let name = li.querySelector('.contact-name-aside').innerText;
    let username = li.getAttribute('data-username');
    let result = confirm(
        `Are you sure you want to delete the contact named ${name}?\nname: ${name}\nusername: ${username}`
    );
    if (result){
        socket.send(JSON.stringify({"type":"delete_contact_request", "username":username}));
        if (li.classList.contains("selected")){
            contactRemoveSelected();
            cleanMainHeader();
            cleanChatUL();
            cleanMainFooter();
        }
        document.querySelector("#contacts").removeChild(li);
    }
}


let lastScrollTop = 0;
let scrollDownIsHandling = false;
let scrollUpIsHandling = false;

function chatULScrollHandler(e){
    if (! chatIsScrollable()){
        return;
    }
    
    if (chat.scrollTop > lastScrollTop){
        // downscroll code
        scrollUpIsHandling = false;
        if (getChatScrollBottom() < 50){
            if (scrollDownIsHandling){
                return;
            }
            scrollDownIsHandling = true;
            console.log(`bottom`); ///
        } 
    }
    else{
        // upscroll code
        scrollDownIsHandling = false;
        if (chat.scrollTop < 10){
            if (scrollUpIsHandling){
                return
            }
            scrollUpIsHandling = true;
            console.log(`top`); 
            //////////////// load messages ////////
            let contact = document.querySelector(`aside li.selected`);
            if (contact === null){
                return;
            }
            loadMessages({
                username:contact.getAttribute("data-username"),
                initial:false,
                since:chat.firstElementChild.getAttribute("data-message-id")
            });
        }
    }

    lastScrollTop = chat.scrollTop <= 0 ? 0 : chat.scrollTop;

}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////// utils ///////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function showCurrentUserData(){
    let current_user_data_div = document.querySelector("#current-user-data");
    let data = `
        <span id="current-user-data-title">current user</span>
        <p id="current-user-username"> username: <span>USERNAME</span> </p>
        <p id="current-user-name"> name: <span>NAME<span> </p>
    `.replace('USERNAME', current_user_username).replace('NAME', current_user_name);
    current_user_data_div.innerHTML = data;
}

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
    <button id="msg-submit" type="submit" onclick="msgSubmitClickHandler(event)">Send</button> 
    `;  
    document.querySelector('#msg-input').focus();
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

function checkClickOnNewContact(aside_li_tag){
    let contact = document.querySelector(`aside li.selected`);
    if (aside_li_tag === contact){
        return false;
    }
    else{
        return true;
    }
}

function contactRemoveSelected(){
    let contact = document.querySelector(`aside li.selected`);
    if (contact !== null){
        contact.classList.remove('selected');
        let username = contact.getAttribute('data-username');
        roomDisconnectRequest(username);
    }
}
function contactAddSelected(aside_li_tag){
    aside_li_tag.classList.add('selected');
    let username = aside_li_tag.getAttribute('data-username');
    roomConnectRequest(username);
    addMainFooter(); 
    addMainHeader({
        'avatar':aside_li_tag.querySelector('img').getAttribute('src'),
        'username':username,
        'roomid':aside_li_tag.getAttribute('data-roomid'),
        'name':aside_li_tag.querySelector('.contact-name-aside').innerText,
        'online_status':''
    });
    cleanChatUL();
    loadMessages({username:username, initial:true});
    // online status, ...  get online status request
}


function loadMessages({username, initial=true, since=null}={}){
    if (isLoadingMessages){
        return;
    }
    socket.send(JSON.stringify({
        "type":"load_messages_request",
        "username":username,
        "initial":initial,
        "since":since // msg id
    }));
}

function truthSocialBotMessage({message='', code=''}={}){
    cleanChatUL();
    cleanMainFooter();
    addMainHeader({
        'avatar':'http://'+window.location.host+'/media/truth_social_media/truth_social_bot.png',
        'name':'truth social',
        'online_status':'always online'
    });
    let currentdate = new Date(); 
    let datetime = standardDateTimeFormat(currentdate);
    console.log(datetime);
    let text = `${message} ${code}`;
    addMessageLI({
        li_class:'you',
        sender_name:'truth social', 
        datetime:datetime,
        text:text
    });

}

function addMessageLI({
    li_class='you', datetime='', sender_name='', message_id='',
    sender_username='', text='', prepend_or_append='append'
}={})
{
    let time = Array.isArray(datetime) ? datetime[0] : datetime;
    let color = 'green';
    if (li_class === 'me'){
        color = 'blue';
    }
    
    let li = `
    <li class="LICLASS" data-username="SENDERUSERNAME" data-message-id="MESSAGEID" data-datetime="DATETIME">
        <div class="entete">
            <h3 style="color:#5e616a;">SHOWDATETIME</h3>
            <h2 style="font-size:17px;">SENDERNAME</h2>
            <span class="status COLOR"></span>
        </div>
        <div class="triangle"></div>
        <div class="message"> 
            MESSAGETEXT
        </div>
    </li>
    `.replace('LICLASS', li_class).replace('SENDERUSERNAME', sender_username
    ).replace('DATETIME', time).replace('SENDERNAME', sender_name
    ).replace('COLOR', color).replace('MESSAGETEXT', text
    ).replace('MESSAGEID', message_id).replace('SHOWDATETIME', time.slice(0, 19)) 

    if (prepend_or_append === 'append'){
        chat_ul.append(li);
    }
    else{
        chat_ul.prepend(li);
    }
     
}

function addContactLI({
    username='', name='', avatar='', roomid='', 
    new_msg_count='', last_msg_time='', prepend_or_append='append'
}={})
{
    let li = `
        <li data-username="USERNAME" data-roomid="ROOMID" data-last-msg-time="LASTMSGTIME" onclick="contactClickHandler(event)" ondblclick="contactDBClickHandler(event)">
            <img src="AVATAR" alt="" width="50" height="50">
            <div>
                <h2 class="contact-name-aside">NAME</h2>
                <h3>
                    <span class="new-messages-number" style="visibility:NMCVISIBILITY;">NEWMSGCOUNT</span> &nbsp&nbsp <span class="last-msg-time">VISUALLASTMSGTIME</span>
                </h3>
            </div>
            <div class="contact-delete-icon-div">
                <i class="material-icons contact-delete-icon" onclick="deleteContactRequestHandler(event)">delete</i>
            </div>
        </li>
    `.replace("USERNAME", username).replace('ROOMID', roomid
    ).replace('AVATAR', avatar).replace('NAME', name
    ).replace('NEWMSGCOUNT', new_msg_count
    ).replace('LASTMSGTIME'. last_msg_time
    ).replace('VISUALLASTMSGTIME', last_msg_time.slice(0, 19)
    ).replace(
        "NMCVISIBILITY", 
        new_msg_count > 0 ? "visible" : "hidden"
    );

    if (prepend_or_append === 'append'){
        contact_ul.append(li);
    }
    else{
        contact_ul.prepend(li);
    }  
}

function updateLastMsgTime({target=null, datetime=''}={}){
    target.setAttribute("data-last-msg-time", datetime);
    target.querySelector(".last-msg-time").innerText = datetime.slice(0, 19);
    $(target).prependTo("#contacts");
}

function updateLastRead(){
    // get selected contact
    //set new msg count to 0 and visibility to hide
    // send request for update last msg time (send contact username as arg)
}

function standardDateTimeFormat(date_obj){

    let month = toTwoDigit(date_obj.getMonth()+1);
    let day = toTwoDigit(date_obj.getDate());
    let hours = toTwoDigit(date_obj.getHours());
    let minutes = toTwoDigit(date_obj.getMinutes());
    let seconds = toTwoDigit(date_obj.getSeconds());

    let datetime =  date_obj.getFullYear() + "-"
                    + month + "-" 
                    + day + " "  
                    + hours + ":"  
                    + minutes + ":" 
                    + seconds + "."
                    + date_obj.getMilliseconds();
    
    return datetime;
}

function getOnlineStatus(username){

}

function roomConnectRequest(username){
    socket.send(JSON.stringify({'type':'room_connect_request', 'username': username}));
}
function roomDisconnectRequest(username){
    socket.send(JSON.stringify({'type':'room_connect_request', 'username': username}));
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

function toTwoDigit(num){ 
    let number = num.toString();
    if (number.length === 2){
        return number;
    }
    return "0" + number;
}

function getChatScrollBottom(){
    // return chat.scrollHeight - (chat.scrollTop + chat.clientHeight)
    return (chat.scrollHeight - chat.clientHeight) - chat.scrollTop;
}

function chatIsScrollable(){
    if (chat.scrollHeight > chat.clientHeight){
        return true;
    }
    return false;
}