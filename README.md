Hello everybody, as mentioned in the about section, the truth social is a social network similar to Twitter with a chat section implemented by django channels.  
(Currently, only the chat part is fully implemented and can be tested.)

## Navigation
- [about chat](#about-chat)
- [Run](#run)
- [endpoints](#endpoints)  


## about chat
When you enter the chat section, a list of users you have talked to will be loaded as contacts.    
You can start a conversation by entering a username.   
You can delete conversations bilaterally.    
Things like notification, is typing, online status, block/unblock, infinit scroll have also been implemented.    
By clicking on a contact, `n` recent messages will be loaded, and by scrolling up, `m` previous messages will be loaded and ... (infinit scroll).   
By sending or receiving a new message, the contacts will be sorted according to the time of the last message.  
Test app chat by opening several incognito windows and logging in with different users.  

## Run  
Clone and cd to the truth_social directory: 
``` bash
git clone git@github.com:mhrashvand1/truth_social.git   

cd truth_social   
```  
Create a virtual environment and install the requirements: 
``` bash  
virtualenv -p python3 venv   

source venv/bin/activate   

pip install -r requirements.txt   

``` 
run postgress and redis:   
``` bash
docker-compose -f docker-compose.dev.yml up -d  
```
create test user:   
You can alse create user by signing up (Go to `swagger/` or `redoc/` to see the corresponding endpoints.)
``` bash 
./manage.py createtestuser <username> <password>
```  

run server: 
``` bash
./manage.py runserver  

```

## endpoints
`chat/`  
`chat/login/`  
`chat/logout/`