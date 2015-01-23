from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/$', 'jmail.macct.views.admin', name='admin'),
    url(r'^create/$', 'jmail.macct.views.create', name='create'),
    url(r'^(\d+)/remove/$', 'jmail.macct.views.remove', name='remove'),
    url(r'^(\d+)/edit/$', 'jmail.macct.views.edit', name='edit'),

    url(r'^(\d+)/subs/$', 'jmail.macct.views.subs', name='subs'),
    url(r'^(\d+)/check/([\w=]+)/$', 'jmail.macct.views.check', name='check'),
)
