from datetime import date, datetime, timedelta

from django.conf import settings

DATE_FORMAT = settings.DATE_FORMAT
DATETIME_FORMAT = settings.DATETIME_FORMAT


def get_date(value):
    error = None
    data = None
    if value:
        try:
            data = datetime.strptime(str(value), DATE_FORMAT)
        except ValueError:
            pass
        try:
            data = datetime.strptime(str(value), '%Y-%m-%d')
        except ValueError:
            pass
        if not data:
            error = 'Неправильный формат даты (дд.мм.гггг)'
    return data, error


def delta_minutes(start, finish):
    if isinstance(start, int):
        start = datetime.strptime(str(start), '%Y%m%d%H%M')
    else:
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M')
    if isinstance(finish, int):
        finish = datetime.strptime(str(finish), '%Y%m%d%H%M')
    else:
        finish = datetime.strptime(finish, '%Y-%m-%dT%H:%M')

    return int((finish - start).seconds / 60)


def add_minutes(time, minutes):
    if isinstance(time, int):
        time = datetime.strptime(str(time), '%Y%m%d%H%M')

    time += timedelta(minutes=minutes)

    return int(time.strftime('%Y%m%d%H%M'))


def get_week_start(day):
    return day - timedelta(days=day.isocalendar()[2] - 1)


def get_datetime_string(value=None, timezone=None, mask=None):
    if not value:
        return ''
    datetime_format = mask if mask else DATETIME_FORMAT
    if timezone:
        value += timedelta(hours=timezone)
    return value.strftime(datetime_format)


def get_month_name(month):
    month_list = [
        '', 'января', 'февраля',
        'марта', 'апреля', 'мая',
        'июня', 'июля', 'августа',
        'сентября', 'октября', 'ноября',
        'декабря'
    ]
    return month_list[int(month)]


def get_month_days(month):
    month_list = [
        '', 'января', 'февраля',
        'марта', 'апреля', 'мая',
        'июня', 'июля', 'августа',
        'сентября', 'октября', 'ноября',
        'декабря'
    ]
    return month_list[int(month)]