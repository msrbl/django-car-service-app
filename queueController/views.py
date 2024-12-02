from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Post, Ticket
from .serializers import TicketSerializer, PostSerializer
from .services import create_ticket, complete_ticket, assign_ticket_to_post

class CreateTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket = create_ticket(request.user)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CompleteTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        ticket = complete_ticket(ticket_id)
        if ticket:
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

class AssignTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        ticket = assign_ticket_to_post(post_id)
        if ticket:
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No ticket to assign or post is occupied'}, status=status.HTTP_400_BAD_REQUEST)
