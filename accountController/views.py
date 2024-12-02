from datetime import timezone
from rest_framework.response import Response
from rest_framework import serializers, status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from appointmentController.models import Appointment
from appointmentController.serializers import AppointmentSerializer
from .utils import TokenGenerator
from .serializers import UserSerializer, LoginSerializer
from .models import User

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        appointments = Appointment.objects.filter(user=user)
        upcoming_appointments = appointments.filter(date__gte=timezone.now()).order_by('date')
        past_appointments = appointments.filter(date__lt=timezone.now()).order_by('-date')
        
        user_data = UserSerializer(user).data
        user_data['upcoming_appointments'] = AppointmentSerializer(upcoming_appointments, many=True).data
        user_data['past_appointments'] = AppointmentSerializer(past_appointments, many=True).data
        
        return Response(user_data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = []
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = []  # Доступно без аутентификации

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = TokenGenerator.for_user(user)
        return Response(token, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)