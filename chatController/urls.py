from django.urls import path
from .views import ChatList, ChatDetail, MessageList

urlpatterns = [
    path('chats/', ChatList.as_view(), name='chat-list'),
    path('chats/<int:chat_id>/', ChatDetail.as_view(), name='chat-detail'),
    path('chats/<int:chat_id>/messages/', MessageList.as_view(), name='message-list'),
]