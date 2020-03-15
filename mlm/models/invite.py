from django.core.exceptions import ValidationError
from django.db import models
from safedelete.models import SafeDeleteModel
from absolutum.mixins import CoreMixin, DisplayMixin


class Invite(SafeDeleteModel, CoreMixin, DisplayMixin):
    """
        МЛМ-приглашение
    """
    INVITE_STATUS = (
        ('wait', 'Ожидание'),
        ('ok', 'Выплата'),
    )
    status = models.CharField(max_length=16, choices=INVITE_STATUS, default='ok', verbose_name='Статус')
    agent = models.ForeignKey('mlm.Agent', related_name='invites', on_delete=models.CASCADE, verbose_name='Агент')
    deal = models.ForeignKey('deal.Deal', related_name='invites', on_delete=models.CASCADE, verbose_name='Сделка')
    level = models.PositiveIntegerField(default=1, verbose_name='Уровень')
    percent = models.PositiveIntegerField(default=0, verbose_name='Процент')
    cost = models.DecimalField(default='0.00', blank=True, max_digits=30, decimal_places=2, verbose_name='Стоимость')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    list_display = ['deal_id', 'deal', 'level', 'percent', 'status', 'cost']
    list_form_fields = ['agent', 'deal', 'level', 'percent', 'cost']

    filters_ordered = ['agent']
    filters_fields = dict(
        agent=dict(
            label='Агента', key='agent',
            widget=dict(attrs={}, name='Select', input_type="select", model_name='mlm.Agent')
        ),
    )
    router_name = 'mlm_invite'

    class Meta:
        verbose_name = 'МЛМ-приглашение'
        verbose_name_plural = 'МЛМ-приглашения'
        default_permissions = ()
        permissions = [
            ('view_invite', 'Просматривать МЛМ-приглашения'),
            ('send_invite', 'Отправлять МЛМ-приглашения'),
        ]

    def __str__(self):
        return '%s (%s)' % (self.deal.cache.get('title'), self.cost)

    def clean(self):
        if Invite.objects.filter(deal=self.deal, level=self.level, deleted=None).exclude(pk=self.id).exists():
            raise ValidationError({'__all__': 'Инвайт уже создан'})
        return super().clean()

    @staticmethod
    def set_invite(deal, agent):
        invite, _ = Invite.objects.get_or_create(agent=agent, deal=deal)
        invite.percent = agent.level_1
        invite.cost = deal.cost / 100 * invite.percent
        invite.save()
        agent.save()  # update agent.cache

        # level 2
        agent_2 = agent.parent
        if agent_2:
            print('agent_2', agent_2)
            invite_2, _ = Invite.objects.get_or_create(agent=agent_2, deal=deal, level=2)
            invite_2.percent = agent_2.level_2
            invite_2.cost = deal.cost / 100 * invite_2.percent
            invite_2.save()
            agent_2.save()  # update agent.cache

        # level 3
        agent_3 = agent_2.parent if agent_2 else None
        if agent_3:
            invite_3, _ = Invite.objects.get_or_create(agent=agent_3, deal=deal, level=3)
            invite_3.percent = agent_3.level_3
            invite_3.cost = deal.cost / 100 * invite_3.percent
            invite_3.save()
            agent_3.save()  # update agent.cache

        return invite

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.agent.save()
