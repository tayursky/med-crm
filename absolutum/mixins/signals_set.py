from sms.models import *


def watch_pre_save(sender, instance, **kwargs):
    # print('\nPRE_SAVE')
    # print('sender', sender)
    # print('instance', instance)
    # print('kwargs', kwargs)
    pass


def deal_post_save(sender, instance, created, **kwargs):
    print('\nPOST_SAVE', created)

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
    pass
