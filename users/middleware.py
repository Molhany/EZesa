from django.shortcuts import redirect
from .models import Profile

class EnsureProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            Profile.objects.get_or_create(user=request.user)
        response = self.get_response(request)
        return response