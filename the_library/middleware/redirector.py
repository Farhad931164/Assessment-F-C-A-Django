from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class RedirectUnauthenticatedMiddleware:
    def __init__(self, get_response):
        self.__user_login_page = False
        self.get_response = get_response
        self.public_urls = [
            reverse(settings.LANDING_PAGE_URL), 
            reverse('admin:login'),                    
        ]
        self.public_url_prefixes = [
            settings.STATIC_URL
        ]

    def __call__(self, request):
        print(request.path)
        if not request.user.is_authenticated:
            is_public_url = any(request.path == url for url in self.public_urls)
            is_public_prefix = any(request.path.startswith(prefix) for prefix in self.public_url_prefixes)
            
            if not is_public_url and not is_public_prefix:
                self.__user_login_page = True
                return redirect(settings.LANDING_PAGE_URL)
        else:  # user authenticated
            if self.__user_login_page:
                self.__user_login_page = False
                return redirect(settings.LOGIN_REDIRECT_URL)
            
        response = self.get_response(request)
        return response