from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/subs/$', 'jmail.mdir.views.subs', name='subs'),
    url(r'^(\d+)/check/([\w=]+)/$', 'jmail.mdir.views.check', name='check'),
)
