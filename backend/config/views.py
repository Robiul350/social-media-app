
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "message": "Social Media API is running successfully!",
        "status": "success"
    })
