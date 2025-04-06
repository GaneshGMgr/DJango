from django.shortcuts import redirect
from django.urls import reverse, Resolver404

class CustomEcommerceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            public_paths = [
                reverse('index'),
                reverse('contact'),
                reverse('login'),
                reverse('signup'),
                reverse('logout'),
            ]
        except Resolver404:
            return self.get_response(request)  # If reverse fails, continue request

        # Allow access to Django admin panel
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Allow public pages
        if request.path in public_paths:
            return self.get_response(request)

        # Require login for protected views
        protected_paths = [
            reverse('checkout'),
            '/order/',
            '/payment/',
            '/order-update/',
            '/admin-panel/',
        ]
        if request.path in protected_paths and not request.user.is_authenticated:
            return redirect(reverse('login'))

        return self.get_response(request)
