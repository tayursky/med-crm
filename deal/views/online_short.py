import json
from datetime import date, datetime, timedelta

from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy

from deal.forms.online import OnlineShortForm
from sms.views.sms import deal_online_created


class OnlineShortTemplateView(TemplateView):
    template_name = 'online_short_done.jinja2'


class OnlineShortView(FormView):
    """
        Онлайн запись
    """
    template_name = 'online_short.jinja2'
    form_class = OnlineShortForm
    success_url = reverse_lazy('online_short_done')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        kwargs.update(dict(
            initial=self.kwargs,
        ))
        return self.form_class(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            deal_online_created(form.save())
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            print(kwargs['form'])
        return super().get_context_data(**kwargs)
