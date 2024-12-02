from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import UserNotificationToken
from django.contrib.auth.models import User

@method_decorator(csrf_exempt, name='dispatch')
class RegisterTokenView(View):
    def post(self, request):
        user_id = request.POST.get('user_id')
        fcm_token = request.POST.get('fcm_token')
        
        try:
            user = User.objects.get(id=user_id)
            UserNotificationToken.objects.update_or_create(user=user, defaults={'fcm_token': fcm_token})
            return JsonResponse({"status": "success"}, status=201)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)