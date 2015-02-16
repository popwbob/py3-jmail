from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'jmail.views.home', name='home'),

    url(r'^user/', include('jmail.user.urls', namespace='user')),
    url(r'^acct/', include('jmail.macct.urls', namespace='macct')),
    url(r'^mdir/', include('jmail.mdir.urls', namespace='mdir')),
    url(r'^msg/', include('jmail.msg.urls', namespace='msg')),

    url(r'^debug/$', 'jmail.views.debug', name='debug'),
    url(r'^admin/', include(admin.site.urls)),
)
