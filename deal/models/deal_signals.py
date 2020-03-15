from mlm.models import Invite


def watch_pre_save(sender, instance, **kwargs):
    # print('\nPRE_SAVE')
    # print('sender', sender)
    # print('instance', instance)
    # print('kwargs', kwargs)
    pass


def deal_pre_save(sender, instance, **kwargs):
    print('\ndeal_pre_save')


def deal_post_save(sender, instance, created, **kwargs):
    if instance.stage.name == 'done' and instance.mlm_agent:
        Invite.set_invite(instance, instance.mlm_agent)
    else:
        instance.invites.all().delete()

    # import ipdb; ipdb.set_trace()
    # print('\nPOST_SAVE', created)
    # if created and instance.start_datetime:
    # sms_template = SmsTemplate.objects.get(name='deal_created')
    # person_primary = instance.persons.filter()

    # text = sms_template.format(
    #     first_name=instance, mo='qwe'
    # )
    # print('sender', sender)
    # print('instance', instance)
    # print('created', created)
    # print('kwargs', kwargs)
