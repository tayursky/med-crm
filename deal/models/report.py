from django.db import models

from deal.models import Deal


class ReportManager(models.Manager):
    def get_queryset(self):
        # return super().get_queryset().filter(step__name__in=['cancel', 'done'])
        return super().get_queryset().all()


class Report(Deal):
    """
        Прокси для отчетов по сделкам
    """
    list_display = ['id', 'branch', 'day', 'manager', 'master', 'persons_string',
                    'cost', 'paid', 'paid_non_cash', 'stage']
    list_form_fields = []
    list_detail_fields = []
    list_attrs = dict(
        start_datetime=dict(input_type='daterange')
    )
    display_labels_map = dict(
        persons_string='Клиенты',
        day='День'
    )

    objects = ReportManager()

    class Meta:
        proxy = True
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        ordering = ['branch', 'start_datetime']
        default_permissions = ()
        permissions = []

    def get_day_display(self):
        try:
            return self.start_datetime.strftime('%d.%m.%Y')
        except AttributeError:
            return ''
