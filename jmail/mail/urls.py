from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/([\w=]+)/(\d+)/source/$', 'jmail.mail.views.source', name='source'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/$', 'jmail.mail.views.read', name='read'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/(html)/$', 'jmail.mail.views.read', name='read_html'),

    url(r'^(\d+)/([\w=]+)/(\d+)/attach/([\w=]+)/$', 'jmail.mail.views.attach', name='attach'),

    url(r'^(\d+)/compose/$', 'jmail.mail.views.compose', name='compose'),
    url(r'^(\d+)/([\w=]+)/(\d+)/reply/$', 'jmail.mail.views.reply', name='reply'),
)
