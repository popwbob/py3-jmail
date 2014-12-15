from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/$', 'jmail.macct.views.check', name='check'),
    url(r'^(\d+)/remove/$', 'jmail.macct.views.remove', name='remove'),
    url(r'^create/$', 'jmail.macct.views.create', name='create'),
)
