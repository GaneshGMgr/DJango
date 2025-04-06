from django.utils import timezone
from django.conf import settings
from datetime import datetime
from django.contrib.auth import logout
from datetime import timedelta
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = [
            reverse('index'),
            reverse('signup'),
            reverse('login'),
            reverse('logout'),
            reverse('request-reset-email'),
        ]
        if request.path.startswith('/admin/') or request.path in public_paths:
            return self.get_response(request)
        
        # ✅ Restrict "/admin-panel/admin-dashboard/" to only active staff members
        if request.path == "/admin-panel/admin-dashboard/":
            if not (request.user.is_authenticated and request.user.is_staff and request.user.is_active):
                return HttpResponseForbidden("<h3>Access Denied: You do not have permission to access this page.</h3>")
            
        if not request.user.is_authenticated:
            return redirect('login')

        return self.get_response(request)
    

class InactivityTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Set a timeout period (e.g., 30 minutes)
            timeout = timedelta(minutes=30)
            last_activity = request.session.get('last_activity')

            if last_activity:
                # Convert the string to a datetime object
                last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                # Make it aware (localize it)
                last_activity = timezone.make_aware(last_activity)

                if timezone.now() - last_activity > timeout:
                    logout(request)
                    return redirect('login')  # Redirect to login page after logout

            # Update the last_activity timestamp
            request.session['last_activity'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        response = self.get_response(request)
        return response