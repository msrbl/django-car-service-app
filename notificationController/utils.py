from django.http import JsonResponse
from pyfcm import FCMNotification
from .models import UserNotificationToken
from django.utils import timezone
from datetime import timedelta

fcm_api_key = 'YOUR_FCM_API_KEY'
push_service = FCMNotification(api_key=fcm_api_key)

def send_notification(token, title, message):
    result = push_service.notify_single_device(registration_id=token, message_title=title, message_body=message)
    return result

def appointment_deleted_notification(user_id, appointment_details):
    try:
        user_token = UserNotificationToken.objects.get(user_id=user_id).fcm_token
        title = "Appointment Deleted"
        message = f"Your appointment: {appointment_details} has been deleted."
        send_notification(user_token, title, message)
    except UserNotificationToken.DoesNotExist:
        pass

def appointment_reminder_notification(user_id, appointment_details):
    try:
        user_token = UserNotificationToken.objects.get(user_id=user_id).fcm_token
        title = "Appointment Reminder"
        message = f"Your appointment: {appointment_details} is in 2 hours."
        send_notification(user_token, title, message)
    except UserNotificationToken.DoesNotExist:
        pass

def chat_message_notification(user_id, chat_message):
    try:
        user_token = UserNotificationToken.objects.get(user_id=user_id).fcm_token
        title = "New Chat Message"
        message = chat_message
        send_notification(user_token, title, message)
    except UserNotificationToken.DoesNotExist:
        pass

def queue_status_notification(user_id, queue_status):
    try:
        user_token = UserNotificationToken.objects.get(user_id=user_id).fcm_token
        title = "Queue Status Update"
        message = queue_status
        send_notification(user_token, title, message)
    except UserNotificationToken.DoesNotExist:
        pass