from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.deprecation import MiddlewareMixin

try:
    auto_login_user = settings.AUTH_AUTOLOGIN_USER
except (AttributeError, ImportError):
    auto_login_user = None


class AutoLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):
        exclude_urls = ['/system/', '/auth/login/', '/cabinet/logout/']
        if auto_login_user and \
                request.user and \
                request.path not in exclude_urls:
            user = get_user_model().objects.get(username=auto_login_user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            print('AutoLoginMiddleware: %s' % request.user)
        # return response
