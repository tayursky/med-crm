import json

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404, JsonResponse, FileResponse, HttpResponse, HttpResponseRedirect
from django.views.generic.base import ContextMixin, TemplateView, View

from django.contrib.auth.mixins import AccessMixin


class LoginRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # def as_view(cls, **initkwargs):
    #     view = super().as_view(**initkwargs)
    #     return login_required(view, login_url='/login/')


def identity_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
