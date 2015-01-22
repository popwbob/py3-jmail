from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #~ url(r'^(\d+)/([a-zA-Z0-9.\-_]+)/(\d+)/$', 'jmail.mail.views.read', name='read'),
    url(r'^(\d+)/([^\/]+)/(\d+)/$', 'jmail.mail.views.read', name='read'),
)
