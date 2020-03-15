# from periods.period import TimeInterval as Period
from django.contrib.auth import views as auth_views
from django.urls import path

from identity.forms import LoginForm
from identity.views.person import PersonSearchView
from identity.views.login import IdentityLoginView, IdentityRecoverView
from absolutum.views import index

urlpatterns = [

    path('person/search/', PersonSearchView.as_view(), name='person_search'),

    path('', IdentityLoginView.as_view(template_name='login.jinja2',
                                       authentication_form=LoginForm,
                                       redirect_authenticated_user=True),
         name='login'
         ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recover/', IdentityRecoverView.as_view(), name='recover'),
]
