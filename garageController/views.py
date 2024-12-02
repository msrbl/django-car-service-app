import requests
from rest_framework import status, views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vehicle
from .serializers import VehicleSerializer

# Внешний API URL и токен
EXTERNAL_API_URL = ""
EXTERNAL_API_TOKEN = ""

class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    #def perform_create(self, serializer):
        vin = self.request.data.get('vin')
        # Запрос к внешнему API
        response = requests.get(
            f"{EXTERNAL_API_URL}/{vin}",
            headers={"Authorization": f"Bearer {EXTERNAL_API_TOKEN}"}
        )
        
        if response.status_code != 200:
            return Response({"error": "Invalid VIN or API error"}, status=status.HTTP_400_BAD_REQUEST)
        
        vehicle_data = response.json()
        make = vehicle_data.get('make')
        model = vehicle_data.get('model')

        serializer.save(user=self.request.user, make=make, model=model)

class VehicleDetailView(generics.RetrieveDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
