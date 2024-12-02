from django.urls import path
from .views import CreateTicketView, CompleteTicketView, AssignTicketView

urlpatterns = [
    path('tickets/create/', CreateTicketView.as_view(), name='create_ticket'),
    path('tickets/complete/<int:ticket_id>/', CompleteTicketView.as_view(), name='complete_ticket'),
    path('tickets/assign/<int:post_id>/', AssignTicketView.as_view(), name='assign_ticket'),
]