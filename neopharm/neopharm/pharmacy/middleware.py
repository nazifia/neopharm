from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if current_time - last_activity > timedelta(minutes=10):
                    logout(request)
                    messages.warning(request, 'Your session has expired due to inactivity. Please login again.')
                    return redirect('store:index')
            
            request.session['last_activity'] = current_time.isoformat()

        response = self.get_response(request)
        return response