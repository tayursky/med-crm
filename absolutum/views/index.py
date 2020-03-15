from django.shortcuts import redirect


def index(request):
    if request.user.is_authenticated:
        person = request.user.person

        if request.user.has_perm('deal.view_deal'):
            return redirect('deal:deal_month')

        elif request.user.is_staff and request.user.is_active and request.user.has_perm('mlm.mlm_manager'):
            return redirect('company:mlm_cabinet_manager')

        elif person.mlm_agent:
            return redirect('partner')

    return redirect('identity:login')
