from rest_framework import serializers
from .models import Service, Work

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['id', 'description']

class ServiceSerializer(serializers.ModelSerializer):
    works = WorkSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'description', 'works', 'created_at']