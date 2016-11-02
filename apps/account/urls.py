from django.conf.urls import url
from django.contrib.auth.views import logout
from emailconfirmation.views import confirm_email

from ajax_validation.views import validate
from account.forms import SignupForm
from . import views

from django.views.generic import TemplateView


class PasswordDeleteView(TemplateView):

    template_name = "account/password_delete_done.html"


urlpatterns = [
    url(r"^email/$", views.email,
        name="acct_email"),
    url(r"^signup/$", views.signup,
        name="acct_signup"),
    url(r"^login/$", views.login,
        name="acct_login"),
    url(r"^login/openid/$", views.login, {"associate_openid": True},
        name="acct_login_openid"),
    url(r"^password_change/$",
        views.password_change, name="acct_passwd"),
    url(r"^password_set/$", views.password_set,
        name="acct_passwd_set"),
    url(r"^password_delete/$", views.password_delete,
        name="acct_passwd_delete"),
    url(r"^password_delete/done/$", PasswordDeleteView.as_view(),
        name="acct_passwd_delete_done"),
    url(r"^timezone/$", views.timezone_change,
        name="acct_timezone_change"),

    url(r"^language/$", views.language_change,
        name="acct_language_change"),
    url(r"^logout/$", logout, {"template_name": "account/logout.html"},
        name="acct_logout"),

    url(r"^confirm_email/(\w+)/$", confirm_email,
        name="acct_confirm_email"),

    # password reset
    url(r"^password_reset/$", views.password_reset,
        name="acct_passwd_reset"),
    url(r"^password_reset/done/$", views.password_reset_done,
        name="acct_passwd_reset_done"),
    url(r"^password_reset_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.password_reset_from_key, name="acct_passwd_reset_key"),

    # ajax validation
    url(r"^validate/$", validate, {"form_class": SignupForm},
        name="signup_form_validate"),
]
