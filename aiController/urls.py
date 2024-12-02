from django.urls import path

from .views import DiagnoseCarIssue

urlpatterns = [
    path('diagnose/', DiagnoseCarIssue.as_view(), name='diagnose_car_issue'),
]