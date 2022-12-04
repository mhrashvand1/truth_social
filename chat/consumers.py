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
from django.db.models import Q, Value, F, Sum, Count, Max, Min, Case, When, DateTimeField

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
            self.username = self.user.username
            self.name = self.user.name
            self.profile = await self.get_user_profile(self.user)
            self.avatar_url = await self.get_abolute_uri(self.profile.avatar.url)
            context = {
                "type":"get_current_user_data",
                "username":self.username,
                "name":self.name,
                "avatar":self.avatar_url
            }
            await self.send(text_data=json.dumps(context))
            await self.channel_layer.group_add(self.user.username, self.channel_name) 
            await self.send_contacts()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user.username, self.channel_name)    
    
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
        msg_text = text_data['text']
        if msg_text.isspace():
            return
        msg_text = msg_text.strip()
        to = text_data['to']  
        
        try:
            destination_user = await sync_to_async(User.objects.get)(username=to)
        except:
            return

        if await self.blocked_you(user=destination_user): # block effect on chat (## oh oh  what about is_blocked???)
            await self.send(text_data=json.dumps({"type":"you_are_blocked", "blocker":to}))
            return
        
        message = {
            'type':'chat_message',
            'text':msg_text,
            'sender_name':self.name,
            'sender_username':self.user.username,
        }     
        common_room = await self.get_pv_common_room(username=to) 
        if common_room:
            # saving message
            msg_obj = await sync_to_async(Message.objects.create)(
                author=self.user, room=common_room, text=msg_text
            )   
            message['datetime'] = str(msg_obj.created_at.astimezone(timezone.get_current_timezone()))
            message['message_id'] = str(msg_obj.id)
            # send notification
            notification_message = {
                "type":"notification",
                "sub_type":"message_notification",
                "username":self.username,
                "datetime":message['datetime']
            }
            await self.channel_layer.group_send(to, {"type":"send_notification_callback", "message":notification_message, "channel_name":self.channel_name})
            # group send msg
            await self.channel_layer.group_send(str(common_room.id), {"type":"send_chat_message_callback", "message":message, "channel_name":self.channel_name})
        else:
            room = await self.create_pv_room(user1=self.user, user2=destination_user)
            # saving message
            msg_obj = await sync_to_async(Message.objects.create)(
                author=self.user, room=room, text=msg_text
            )   
            message['datetime'] = str(msg_obj.created_at.astimezone(timezone.get_current_timezone()))
            message['message_id'] = str(msg_obj.id)
            # group send msg
            await self.channel_layer.group_send(str(room.id), {"type":"send_chat_message_callback", "message":message, "channel_name":self.channel_name})
            # send add room msg
            await self.send_new_contact(
                destination_user=destination_user,
                datetime=message['datetime'],
                room_id=str(room.id)
            )
   
        
        
    async def search_username_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        if self.username == username.lower():
            return  
        
        context = dict()
        context['type'] = 'search_username' 
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
        
        
        
    async def delete_contact_request_handler(self, text_data=None, byte_data=None):
        username = text_data.get('username')
        room = await self.get_pv_common_room(username=username)
        if not room:
            return
        await sync_to_async(room.delete)() 
        message = {
            "type":"delete_contact",
            "username":self.username
        }
        await self.channel_layer.group_send(
            username,
            {
                "type":"send_delete_contact_callback",
                "message":message,
                "channel_name":self.channel_name
            }
        )
        
            
        
    async def load_messages_request_handler(self, text_data=None, byte_data=None):
        username = text_data.get("username")
        room = await self.get_pv_common_room(username=username)
        if not room:
            return 
        
        initial = text_data.get("initial")
        if not isinstance(initial, bool):
            return
        
        if initial: 
            messages = room.messages.order_by("-id")[:10]  # min 10 because page must be scrollable.
        else:
            since = text_data.get("since")
            if not since.isnumeric():
                return
            messages = room.messages.filter(id__lt=int(since)).order_by("-id")[:7]
            
        msg_list = await sync_to_async(list)(messages)        
        final_result = list()
        
        for msg in msg_list:
            result = dict()
            result["text"] = msg.text 
            result["datetime"] = str(msg.created_at.astimezone(timezone.get_current_timezone())),
            result["message_id"] = str(msg.id)
            author = await sync_to_async(self.get_message_author)(msg)    
            result["sender_name"] = author.name,
            result["sender_username"] = author.username
            final_result.append(result)
        
        context = {"type":"load_messages", "results":final_result, "initial":initial}
        await self.send(text_data=json.dumps(context))
        
    
    
    async def update_last_read_handler(self, text_data=None, byte_data=None):
        username = text_data.get("username")
        room = await self.get_pv_common_room(username=username)
        if not room:
            return 
        
        last_msg = await sync_to_async(room.messages.last)()
        if not last_msg:
            return
        last_msg_time = last_msg.created_at
        
        room_user_obj = await sync_to_async(self.get_room_user_obj)(room=room)
        room_user_obj.last_read = last_msg_time
        await sync_to_async(room_user_obj.save)()
        
    ##############################################################################
    ##############################################################################
    ##############################################################################
    ########################### callbacks ########################################
    ##############################################################################
    ##############################################################################
    ##############################################################################

    async def send_chat_message_callback(self, event):
        message = event["message"]        
        await self.send(text_data=json.dumps(message))
        
    async def send_new_contact_callback(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
            
    async def send_delete_contact_callback(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
        
    async def send_notification_callback(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
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
            profile = await self.get_user_profile(user)
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
            last_message_time=Max('messages__created_at', default=F("created_at"))
        ).order_by("-last_message_time")
        
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
        current_user_username = self.username
        current_user_rooms = await self.get_user_rooms(user=current_user)
        current_user_rooms_list = await sync_to_async(list)(current_user_rooms)
        final_result = list()
        
        for room in current_user_rooms_list:
            result = dict()
            result['room_id'] = str(room.id)
            
            last_message_time = room.last_message_time
            if last_message_time:
                result['last_message_time'] = str(
                    last_message_time.astimezone(timezone.get_current_timezone())
                )

            try:
                room_user_obj = await sync_to_async(RoomUser.objects.get)(
                    room=room, user=current_user
                )
                another_user = await sync_to_async(room.members.get)(
                    ~Q(username=current_user_username)
                )
                another_user_profile = await self.get_user_profile(user=another_user)
            except:
                continue
            
            new_messages = Message.objects.filter(created_at__gt=room_user_obj.last_read, room=room)
            result['new_msg_count'] = await sync_to_async(new_messages.count)()
    
            result['username'] = str(another_user.username)
            result['name'] = str(another_user.name)
            result['avatar'] = await self.get_abolute_uri(another_user_profile.avatar.url)
            final_result.append(result)
            
        context = {"type":"load_contacts", "results":final_result}
        await self.send(text_data=json.dumps(context))
        
    
    async def blocked_you(self, user):    
        blockings_queryset = user.blockings.filter(username=self.username)
        result = await sync_to_async(blockings_queryset.exists)()
        return result
    
    async def create_pv_room(self, user1, user2):
        room = await sync_to_async(Room.objects.create)()
        await sync_to_async(RoomUser.objects.create)(room=room, user=user1)
        await sync_to_async(RoomUser.objects.create)(room=room, user=user2)
        return room
    
    async def get_user_profile(self, user):
        profile = await sync_to_async(Profile.objects.get)(user=user)
        return profile
    
    async def send_new_contact(
        self, destination_user, datetime, room_id
    ):
        destination_user_profile = await self.get_user_profile(destination_user)
        
        # send for current user
        message = {
            "type":"add_contact",
            "actor":self.username,
            "username":destination_user.username,
            "name":destination_user.name,
            "avatar":await self.get_abolute_uri(destination_user_profile.avatar.url),
            "room_id":room_id,
            "last_message_time":datetime,
            "new_msg_count":1
        }
        await self.send(text_data=json.dumps(message))
        
        # send for destination user
        message = {
            "type":"add_contact",
            "actor":self.username,
            "username":self.username,
            "name":self.name,
            "avatar":self.avatar_url,
            "room_id":room_id,
            "last_message_time":datetime,
            "new_msg_count":1
        }
        await self.channel_layer.group_send(
            destination_user.username,
            {"type":"send_new_contact_callback", "message":message, "channel_name":self.channel_name}
        )
        
    def get_message_author(self, msg):
        return msg.author
    
    def get_room_user_obj(self, room):
        try:
            room_user = RoomUser.objects.get(room=room, user=self.user)
            return room_user
        except:
            return