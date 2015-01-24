from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/check/([\w=]+)/$', 'jmail.mbox.views.check', name='check'),
)
