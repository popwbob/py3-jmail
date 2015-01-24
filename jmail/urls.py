from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'jmail.views.home', name='home'),

    url(r'^user/', include('jmail.user.urls', namespace='user')),
    url(r'^acct/', include('jmail.macct.urls', namespace='macct')),
    url(r'^mbox/', include('jmail.mbox.urls', namespace='mbox')),
    url(r'^mail/', include('jmail.mail.urls', namespace='mail')),

    url(r'^debug/$', 'jmail.views.debug', name='debug'),
    url(r'^admin/', include(admin.site.urls)),
)
