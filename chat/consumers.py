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
from django.db.models import Q, Value, F, Sum, Count, Max, Min

User = get_user_model()


# self.close()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.user = self.scope['user']                
        if not self.user.is_authenticated:
            message = {
                "type":"user_not_authenticated",
            }
            await self.send(text_data=json.dumps(message))
            await self.close()
        else:
            self.current_user_username = self.user.username
            context = {
                "type":"get_current_user_data",
                "username":self.current_user_username,
                "name":self.user.name
            }
            await self.send(text_data=json.dumps(context))
            await self.channel_layer.group_add(self.user.username, self.channel_name) ##
            await self.send_contacts()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user.username, self.channel_name) ##    
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        await getattr(self, f"{text_data['type']}_handler")(text_data, bytes_data)


    ##############################################################################
    ##############################################################################
    ##############################################################################
    ############################# handlers #######################################
    ##############################################################################
    ##############################################################################
    ##############################################################################

    async def chat_message_handler(self, text_data=None, byte_data=None):
        if text_data['text'].isspace():
            return
        text_data['text'] = text_data['text'].strip()
        #
        #
        message = {
            'type':'chat_message',
            'text':text_data['text'],
            'datetime':str(timezone.now().now()),
            'sender_name':self.user.name,
            'sender_username':self.user.username,
            'message_id':'', ##
        }
        await self.send(text_data=json.dumps(message)) ##
        
        
    async def search_username_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        context = dict()
        context['type'] = 'search_username' 
        current_user = self.user   
        if current_user.username == username.lower():
            return    
        try:
            user = await sync_to_async(User.objects.get)(username=username)
            data = await self.serialize_user(user)
            context = {**context, **data}
            context['status'] = 200
        except User.DoesNotExist:
            context['status'] = 404
            context['username'] = username
        await self.send(text_data=json.dumps(context))
    
    
    async def room_disconnect_request_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        room = await self.get_pv_common_room(username=username)  
        if room:
            await self.channel_layer.group_discard(str(room.id), self.channel_name) 
            await self.channel_layer.group_discard(f"online_status_{username}", self.channel_name)       
    
    async def room_connect_request_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        room = await self.get_pv_common_room(username=username)  
        if room:
            await self.channel_layer.group_add(str(room.id), self.channel_name)  
            await self.channel_layer.group_add(f"online_status_{username}", self.channel_name)       
        
    ##############################################################################
    ##############################################################################
    ##############################################################################
    ########################### callbacks ########################################
    ##############################################################################
    ##############################################################################
    ##############################################################################




    ##############################################################################
    ##############################################################################
    ##############################################################################
    ################################## utils #####################################
    ##############################################################################
    ##############################################################################
    ##############################################################################
        
        
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
    
    
    async def get_user_rooms(self, user=None, username=None):
        if user:
            user_rooms = Room.objects.filter(members=self.user)
        elif username:
            user_rooms = Room.objects.filter(members__username=self.user) 
        else:
            return Room.objects.none()

        user_rooms = user_rooms.annotate(
            last_message_time=Max('messages__created_at')
        ).order_by("-messages__created_at")
        
        return user_rooms
    
    
    async def get_pv_common_room(self, username):
        current_user_rooms = await self.get_user_rooms(user=self.user)
        try:
            common_room = await sync_to_async(current_user_rooms.get)(
                members__username=username
            )
            return common_room
        except:
            print(f'Error finding pv common room between user={self.user.username}, user={username} ')
        
        
    async def send_contacts(self):
        current_user = self.user
        current_user_username = current_user.username
        current_user_rooms = await self.get_user_rooms(user=current_user)
        current_user_rooms_list = await sync_to_async(list)(current_user_rooms)
        final_result = list()
        
        for room in current_user_rooms_list:
            result = dict()
            result['room_id'] = str(room.id)
            result['last_message_time'] = str(
                room.last_message_time.astimezone(timezone.get_current_timezone())
            )

            try:
                room_user_obj = await sync_to_async(RoomUser.objects.get)(
                    room=room, user=current_user
                )
                another_user = await sync_to_async(room.members.get)(
                    ~Q(username=current_user_username)
                )
                another_user_profile = await sync_to_async(Profile.objects.get)(
                    user=another_user
                )
            except:
                continue
            
            new_messages = Message.objects.filter(created_at__gt=room_user_obj.last_read, room=room)
            result['new_msg_count'] = await sync_to_async(new_messages.count)()
    
            result['username'] = str(another_user.username)
            result['name'] = str(another_user.username)
            result['avatar'] = await self.get_abolute_uri(another_user_profile.avatar.url)
            final_result.append(result)
            
        context = {"type":"load_contacts", "results":final_result}
        await self.send(text_data=json.dumps(context))
        
   