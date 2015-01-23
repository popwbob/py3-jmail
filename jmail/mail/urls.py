from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/([^\/]+)/(\d+)/source/$', 'jmail.mail.views.source', name='source'),

    #~ url(r'^(\d+)/([a-zA-Z0-9.\-_]+)/(\d+)/$', 'jmail.mail.views.read', name='read'),
    url(r'^(\d+)/([^\/]+)/(\d+)/read/$', 'jmail.mail.views.read', name='read'),
)
