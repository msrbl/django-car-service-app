from rest_framework import serializers
from .models import Ticket, Post

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'user', 'appointment', 'status', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'name', 'is_occupied', 'ticket']