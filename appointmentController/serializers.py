from rest_framework import serializers

from garageController.models import Vehicle
from .models import CarMake, CarModel, Appointment

class CarMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMake
        fields = ['id', 'name']

class CarModelSerializer(serializers.ModelSerializer):
    make = CarMakeSerializer()

    class Meta:
        model = CarModel
        fields = ['id', 'make', 'name']

class AppointmentSerializer(serializers.ModelSerializer):
    make = serializers.CharField(required=False, allow_blank=True)
    model = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'make', 'model', 'date', 'time', 'comment', 'services', 'is_live_queue', 'is_completed']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        make = validated_data.pop('make', None)
        model = validated_data.pop('model', None)
        
        appointment = Appointment.objects.create(user=user, make=make, model=model, **validated_data)
        return appointment
    
class LiveQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'user', 'date', 'time', 'is_live_queue', 'is_completed']