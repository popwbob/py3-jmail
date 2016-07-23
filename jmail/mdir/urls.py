from django.conf.urls import url
from jmail.mdir import views

urlpatterns = [
    url(r'^(\d+)/subs/$', views.subs, name='subs'),
    url(r'^(\d+)/check/([\w=]+)/$', views.check, name='check'),
]
