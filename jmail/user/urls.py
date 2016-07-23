from django.conf.urls import url
from jmail.user import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^logout/$', views.logout, name='logout'),
]
