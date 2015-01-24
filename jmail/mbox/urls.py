from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/subs/$', 'jmail.mbox.views.subs', name='subs'),
    url(r'^(\d+)/check/([\w=]+)/$', 'jmail.mbox.views.check', name='check'),
)
