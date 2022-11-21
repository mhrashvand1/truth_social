from channels.consumer import AsyncConsumer
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from chat.models import Room, Message, RoomUser
from django.contrib.auth import get_user_model
from activity.models import OnlineStatus, Block
from django.utils import timezone

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

    # handlers
    async def msg_handler(self, text_data=None, byte_data=None):
        message = {
            'type':'msg',
            'text':text_data['text'],
            'datetime':str(timezone.now().now())[:19]
        }
        await self.send(text_data=json.dumps(message))
        
    async def search_username_handler(self, text_data=None, byte_data=None):
        pass
        
    # callbacks
    