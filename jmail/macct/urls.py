from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/$', 'jmail.macct.views.check', name='check'),
)
