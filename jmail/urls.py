from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'jmail.views.home', name='home'),
    url(r'^debug/$', 'jmail.views.debug', name='debug'),
    url(r'^admin/', include(admin.site.urls)),
)
