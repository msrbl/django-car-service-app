from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarMakeViewSet, CarModelViewSet, AppointmentViewSet, LiveQueueViewSet

router = DefaultRouter()
router.register(r'car-makes', CarMakeViewSet)
router.register(r'car-models', CarModelViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'live-queue', LiveQueueViewSet, basename='live-queue')

urlpatterns = [
    path('', include(router.urls)),
]