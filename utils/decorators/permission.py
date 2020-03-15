from datetime import date, datetime, timedelta
from functools import wraps

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response


def perm_required(perm):
    def decorator(dispatch):
        @wraps(dispatch, perm)
        def _wrapped_func(cls, request, *args, **kwargs):
            # print(perm)
            # print(cls)
            # import ipdb; ipdb.set_trace()

            if not request.GET and not request.POST:
                return render(request, 'app_vue.jinja2')

            if not request.user.has_perm(perm):
                return JsonResponse(dict(error='Недостаточно прав доступа'))


            return dispatch(cls, request, *args, **kwargs)

        return _wrapped_func
    return decorator
