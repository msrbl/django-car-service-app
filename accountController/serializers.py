from rest_framework import serializers
from .models import User

from django.contrib.auth import authenticate
from .utils import TokenGenerator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')

        if phone and password:
            user = authenticate(request=self.context.get('request'), phone=phone, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Must include "phone" and "password"')

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        token = TokenGenerator.for_user(user)
        return token