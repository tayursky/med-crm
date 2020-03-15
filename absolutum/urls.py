"""absolutum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, include

from absolutum.views.spider import SpiderView, SpiderPartnerView
from absolutum.views.routes import GetRoutes, GetSettings
from deal.views.online_short import OnlineShortView, OnlineShortTemplateView
from deal.views.online_spider import OnlineSpiderView, OnlineSpiderPartnerView
from identity.forms import LoginForm
from absolutum.views import index
from mlm.views.agent_cabinet import AgentOfferView, AgentRegistrationView, AgentHelpView, AgentCabinetView
from mlm.views.invite import InviteView

urlpatterns = [
    path('get_settings/', GetSettings.as_view(), name='get_settings'),
    path('get_routes/', GetRoutes.as_view(), name='get_menu'),
    path('company/', include(('company.urls', 'company'), namespace='company-urls')),
    path('deal/', include(('deal.urls', 'deal'), namespace='deal-urls')),
    path('directory/', include(('directory.urls', 'directory'), namespace='directory-urls')),
    path('identity/', include(('identity.urls', 'identity'), namespace='identity-urls')),
    path('sip/', include(('sip.urls', 'sip'), namespace='sip-urls')),
    path('sms/', include(('sms.urls', 'sms'), namespace='sms-urls')),

    # path('partner/registration/', AgentRegistrationView.as_view(), name='partner_registration'),
    path('partner/invite/<str:token>/', InviteView.as_view(), name='partner_invite'),
    path('partner/offer/', AgentOfferView.as_view(), name='partner_offer'),
    path('partner/help/', AgentHelpView.as_view(), name='partner_help'),
    path('partner/', AgentCabinetView.as_view(), name='partner'),
    path('mlm/', include(('mlm.urls', 'mlm'), namespace='mlm-urls')),

    path('login/', auth_views.LoginView.as_view(template_name='login.jinja2', authentication_form=LoginForm,
                                                redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('admin/', admin.site.urls),

    path('test/', SpiderView.as_view(), name='spider'),
    path('test_partner/', SpiderPartnerView.as_view(), name='spider_partner'),
    path('spider/', OnlineSpiderView.as_view(), name='online_spider'),
    path('spider_partner/', OnlineSpiderPartnerView.as_view(), name='online_spider_partner'),
    path('online_done/', OnlineShortTemplateView.as_view(), name='online_short_done'),
    path('online/', OnlineShortView.as_view(), name='online_short'),
    path('online/<str:promocode>/', OnlineShortView.as_view(), name='online_promo'),
    path('invite/', OnlineShortView.as_view(), name='invite_short'),
    path('invite/<str:promocode>/', OnlineShortView.as_view(), name='invite_promo'),

    path('', index.index, name='index'),
    # path('', lambda request: redirect('deal:deal_month'), name='index_redirect'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
