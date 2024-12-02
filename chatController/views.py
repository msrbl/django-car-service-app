from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from aiController.views import DiagnoseCarIssue
from accountController.models import User
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

class ChatList(APIView):
    # Метод для получения всех чатов пользователя
    def get(self, request, *args, **kwargs):
        user = request.user
        chats = Chat.objects.filter(user=user)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    # Метод для создания нового чата
    def post(self, request, *args, **kwargs):
        user = request.user
        chat_type = request.data.get('chat_type')
        manager_id = request.data.get('manager_id', None)
        
        # Проверка, если тип чата - "admin", то должен быть указан manager_id
        if chat_type == 'admin' and manager_id is None:
            return Response({"error": "Manager ID is required for admin chat"}, status=status.HTTP_400_BAD_REQUEST)
        
        chat = Chat.objects.create(user=user, manager_id=manager_id, chat_type=chat_type)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatDetail(APIView):
    # Метод для получения объекта чата по его ID
    def get_chat(self, chat_id):
        try:
            return Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return None

    # Метод для получения деталей чата
    def get(self, request, chat_id, *args, **kwargs):
        chat = self.get_chat(chat_id)
        if not chat:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)

    # Метод для удаления чата
    def delete(self, request, chat_id, *args, **kwargs):
        chat = self.get_chat(chat_id)
        if not chat:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageList(APIView):
    # Метод для отправки сообщения в чат
    def post(self, request, chat_id, *args, **kwargs):
        chat = Chat.objects.get(id=chat_id)
        sender = request.user
        text = request.data.get('text')

        # Если чат с типом "ai", то отправляем запрос к ИИ
        if chat.chat_type == 'ai':
            ai_response = DiagnoseCarIssue(text)
            ai_user = User.objects.get(username='AI')
            
            # Создаем сообщение от пользователя
            user_message = Message.objects.create(chat=chat, sender=sender, text=text)
            # Создаем сообщение от ИИ
            ai_message = Message.objects.create(chat=chat, sender=ai_user, text=ai_response)

            user_serializer = MessageSerializer(user_message)
            ai_serializer = MessageSerializer(ai_message)

            return Response({
                "user_message": user_serializer.data,
                "ai_message": ai_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # Создаем обычное сообщение
            message = Message.objects.create(chat=chat, sender=sender, text=text)
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)