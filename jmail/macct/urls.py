from django.conf.urls import url
from jmail.macct import views

urlpatterns = [
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^create/$', views.create, name='create'),
    url(r'^(\d+)/remove/$', views.remove, name='remove'),
    url(r'^(\d+)/edit/$', views.edit, name='edit'),
]
