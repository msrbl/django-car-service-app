from datetime import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from accountController.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from garageController.models import Vehicle
from .models import CarMake, CarModel, Appointment
from .serializers import CarMakeSerializer, CarModelSerializer, AppointmentSerializer, LiveQueueSerializer

class CarMakeViewSet(viewsets.ModelViewSet):
    queryset = CarMake.objects.all()
    serializer_class = CarMakeSerializer
    permission_classes = [IsAdminOrReadOnly]

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = [IsAdminOrReadOnly]

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly, IsOwnerOrAdmin]

    def get_queryset(self):
        # Админ видит все посещения, клиенты - только свои
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LiveQueueViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Получаем текущую очередь живой очереди
        queue = Appointment.objects.filter(is_live_queue=True, is_completed=False).order_by('date', 'time')
        serializer = LiveQueueSerializer(queue, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Создание нового талона в живую очередь
        user = request.user

        try:
            vehicle = Vehicle.objects.get(user=user)
            make = vehicle.make
            model = vehicle.model
        except Vehicle.DoesNotExist:
            make = None
            model = None
            
        appointment = Appointment.objects.create(
            user=user,
            make=make,
            model=model,
            date=timezone.now().date(),
            time=timezone.now().time(),
            comment='',
            is_live_queue=True
        )
        serializer = LiveQueueSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # Завершение текущего талона и перемещение следующего в очередь
        try:
            appointment = Appointment.objects.get(pk=pk, is_live_queue=True, is_completed=False)
            appointment.complete_appointment()
            
            # Перемещение следующего талона
            next_appointment = Appointment.get_next_in_queue()
            if next_appointment:
                next_appointment.time = timezone.now().time()
                next_appointment.save()
                
            return Response(status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found or already completed"}, status=status.HTTP_404_NOT_FOUND)