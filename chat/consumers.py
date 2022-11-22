from channels.consumer import AsyncConsumer
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from chat.models import Room, Message, RoomUser
from django.contrib.auth import get_user_model
from activity.models import OnlineStatus, Block
from django.utils import timezone
from account.models import Profile

User = get_user_model()


# self.close()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        user = self.scope['user']                

        if not user.is_authenticated:
            message = {
                "type":"user_not_authenticated",
            }
            await self.send(text_data=json.dumps(message))
            await self.close()
        else:
            context = {
                "type":"get_current_user_data",
                "username":user.username,
                "name":user.name
            }
            await self.send(text_data=json.dumps(context))


    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        await getattr(self, f"{text_data['type']}_handler")(text_data, bytes_data)


    async def disconnect(self, close_code):
        pass

    ################
    ### handlers ###
    ################
    
    async def chat_message_handler(self, text_data=None, byte_data=None):
        message = {
            'type':'chat_message',
            'text':text_data['text'],
            'datetime':str(timezone.now().now())[:19]
        }
        await self.send(text_data=json.dumps(message)) ##
        
    async def search_username_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        context = dict()
        context['type'] = 'search_username' 
        current_user = self.scope['user']
        
        if current_user.username == username.lower():
            return
        
        try:
            user = await sync_to_async(User.objects.get)(username=username)
            data = await self.serialize_user(user)
            context = {**context, **data}
            context['status'] = 200
        except User.DoesNotExist:
            context['status'] = 404

        await self.send(text_data=json.dumps(context))
    
    #################   
    ### callbacks ###
    #################



    ##################
    ##### utils ######
    ##################
    
    async def serialize_user(self, user):
        result = dict()
        result['name'], result['username'] = user.name, user.username  
        
        try:
            profile = await sync_to_async(Profile.objects.get)(user=user)
            result['avatar'] = await self.get_abolute_uri(url=profile.avatar.url)
        except Profile.DoesNotExist:
            result['avatar'] = ''
        try:
            online_status = await sync_to_async(OnlineStatus.objects.get)(user=user)
            result['online_status'] = dict(OnlineStatus.status_choices)[online_status.status]
        except OnlineStatus.DoesNotExist:
            result['online_status'] = ''
            
        return result
    
    async def get_abolute_uri(self, url):
        scope = self.scope
        server = f"{scope['server'][0]}:{scope['server'][1]}"
        result = f"http://{server}{url}"  ##
        return result