from django.urls import path
from .views import ServiceListView, ServiceDetailView

urlpatterns = [
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
]
