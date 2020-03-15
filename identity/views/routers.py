from directory.utils import get_menu_items

USER_ITEMS = get_menu_items([
    dict(
        name='user',
        label='Пользователь',
        float_right=True,
        subitems=[
            # dict(label=u'Личный кабинет', url='/identity/private/'),
            # dict(split=True),
            dict(label=u'Выйти', url='/logout/'),
        ])
])
