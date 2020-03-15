from django.http import JsonResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist

from company.views.routers import COMPANY_ITEMS
from deal.views.routers import DEAL_ITEMS
from directory.views.routers import DIRECTORY_ITEMS
from identity.views.routers import USER_ITEMS

ROUTES = [
    DEAL_ITEMS[0],
    DIRECTORY_ITEMS[0],
    COMPANY_ITEMS[0],
    USER_ITEMS[0]
]


class GetRoutes(View):
    menu_set = None

    def dispatch(self, request, *args, **kwargs):
        self.menu_set = dict(
            dynamic=[],
            top=[]
        )
        user_perms = request.user.get_all_permissions()

        for index, item in enumerate(ROUTES):
            if item['name'] == 'user':
                item['label'] = request.user.username
            _item = item.copy()
            _item.update(dict(subitems_list=[], subitems=[]))

            for subitem in item.get('subitems', dict()):
                if subitem.get('perm') and subitem.get('perm') not in user_perms:
                    continue
                if 'router_name' in subitem:
                    _item['subitems_list'].append(subitem['router_name'])
                for sub_subitem in subitem.get('subitems_list', []):
                    _item['subitems_list'].append(sub_subitem)
                _item['subitems'].append(subitem)

            if len(_item['subitems']):
                self.menu_set['top'].append(_item)

        # TODO: понять почему при перелогировании не доходит до item['label'] == 'user', ниже костыль
        self.menu_set['top'][-1]['label'] = request.user.username

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.menu_set, safe=False)


class GetSettings(View):
    data = dict(settings=dict(), permissions=[])

    def dispatch(self, request, *args, **kwargs):
        account = request.user
        person = account.person
        self.data = dict(
            settings=dict(sip_id=person.sip_id),
            permissions=[p for p in account.get_all_permissions()]
        )
        try:
            self.data['settings']['mlm_agent'] = person.mlm_agent.id
        except ObjectDoesNotExist:
            pass

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return JsonResponse(self.data, safe=False)
