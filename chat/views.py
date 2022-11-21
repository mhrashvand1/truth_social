from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.views.generic import View
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q 



class ChatView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'chat/chat.html')