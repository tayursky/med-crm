from company.models import Branch
from deal.models import Stage, ExpenseType, \
    ServiceGroup, Service, ServiceMaster, ServiceTimetable
from directory.utils import get_menu_items
from directory.models import City, WorkingDaysCalendar
from sms.models import SmsTemplate
from sip.models import MightyCallUser, Log as SipLog

DIRECTORY_ITEMS = get_menu_items([
    dict(
        name='directory',
        label='Справочники',
        url='/directory',
        icon='el-icon-notebook-1',
        subitems=[
            # dict(model=Person, perm='identity.view_person'),
            # dict(model=Phone),
            # dict(model=Email),
            # dict(model=UserDisplay),
            dict(model=City),
            dict(model=Branch),
            dict(model=ServiceGroup),
            dict(model=Service),
            dict(model=ServiceMaster),
            dict(model=Stage),
            # dict(split=True, model=Department),
            dict(split=True,
                 model=ExpenseType),
            # dict(model=ServiceTimetable),
            dict(split=True,
                 model=WorkingDaysCalendar, router_name='working_calendar'),
            dict(model=SmsTemplate),
            dict(model=MightyCallUser),
            dict(model=SipLog),
            # dict(model=User),
        ]
    ),
])
