from django.conf.urls import url
from . import views

urlpatterns = [
    url('^change/$', views.change, name='avatar_change'),
    url('^delete/$', views.delete, name='avatar_delete'),
]
