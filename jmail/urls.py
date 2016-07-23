from django.conf.urls import include, url
from django.contrib import admin
from jmail import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^user/', include('jmail.user.urls', namespace='user')),
    url(r'^acct/', include('jmail.macct.urls', namespace='macct')),
    url(r'^mdir/', include('jmail.mdir.urls', namespace='mdir')),
    url(r'^msg/', include('jmail.msg.urls', namespace='msg')),

    url(r'^debug/$', views.debug, name='debug'),
    url(r'^admin/', include(admin.site.urls)),
]
