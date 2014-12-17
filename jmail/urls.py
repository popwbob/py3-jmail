from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'jmail.views.home', name='home'),
    url(r'^debug/$', 'jmail.views.debug', name='debug'),

    url(r'^user/', include('jmail.user.urls', namespace='user')),
    url(r'^macct/', include('jmail.macct.urls', namespace='macct')),
    url(r'^mail/', include('jmail.mail.urls', namespace='mail')),

    url(r'^admin/', include(admin.site.urls)),
)
