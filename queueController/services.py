from .models import Ticket, Post
from django.conf import settings

LifeQueue = []

def create_ticket(user):
    ticket = Ticket.objects.create(user=user)
    LifeQueue.append(ticket)
    return ticket

def get_next_ticket():
    if LifeQueue:
        next_ticket = LifeQueue.pop(0)
        return next_ticket
    return None

def complete_ticket(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    if ticket.post:
        ticket.post.is_occupied = False
        ticket.post.save()
    ticket.status = 'completed'
    ticket.save()
    return ticket

def assign_ticket_to_post(post_id):
    post = Post.objects.get(id=post_id)
    if not post.is_occupied:
        next_ticket = get_next_ticket()
        if next_ticket:
            next_ticket.post = post
            next_ticket.status = 'in_service'
            next_ticket.save()
            post.is_occupied = True
            post.save()
            return next_ticket
    return None
