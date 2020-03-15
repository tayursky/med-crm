SECRET_KEY = '****************************************************'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'work',
        'USER': 'user',
        'PASSWORD': '***',
        'HOST': '',
        'PORT': '5432',
        'CONN_MAX_AGE': None,
    }
}

DATE_FORMAT = '%d.%m.%Y'
DATETIME_FORMAT = '%d.%m.%Y %H:%M'
TIME_FORMAT = '%H:%M'

TEMP_DIR = './tmp'
DOWNLOAD_DIR = './static/download'
EXTRA_INSTALLED_APPS = []

CSRF_DISABLE = True
SMS_TEST = True

# Mango-office
MANGO_ENABLE = False
# Уникальный код АТС
MANGO_API_KEY = '***'
# Ключ для создания подписи
MANGO_API_SALT = '***'

# Yandex Mighty Call
MIGHTY_CALL_ENABLE = True
MIGHTY_CALL_SET = dict(
    api_key='***',  # Уникальный ключ
    version='v3',  # Версия API
    prefix='api'  # Префикс окружения: sandbox или api
)

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = '***@yandex.ru'
EMAIL_HOST_PASSWORD = '***'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

MLM_PAYDAY = 14
MLM_DISCOUNT = 10
MLM_LEVEL_1_RATE, MLM_LEVEL_2_RATE, MLM_LEVEL_3_RATE = 5, 5, 5
MLM_MANAGER_PERCENT = ((500000, 3), (600000, 4), (700000, 5), (800000, 6), (900000, 7), (1000000, 8),
                       (1100000, 9), (12000000, 12))

# Авто-авторизация пользователя
AUTH_NOPASSWORD = True
AUTH_AUTOLOGIN_USER = 'root'
