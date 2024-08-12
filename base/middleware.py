# Create a file named `middleware.py` in one of your apps
from django.conf import settings

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
            print('ADMIN SESSION')
        else:
            settings.SESSION_COOKIE_NAME = 'sessionid'
            print('=============\nUSER SESSION\n==================')

        response = self.get_response(request)
        return response
