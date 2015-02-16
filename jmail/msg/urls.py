from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/([\w=]+)/(\d+)/source/$', 'jmail.msg.views.source', name='source'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/$', 'jmail.msg.views.read', name='read'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/(html)/$', 'jmail.msg.views.read', name='read_html'),

    url(r'^(\d+)/([\w=]+)/(\d+)/attach/([\w=]+)/$', 'jmail.msg.views.attach', name='attach'),

    url(r'^(\d+)/compose/$', 'jmail.msg.views.compose', name='compose'),
    url(r'^(\d+)/send/$', 'jmail.msg.views.send', name='send'),

    url(r'^(\d+)/([\w=]+)/(\d+)/reply/$', 'jmail.msg.views.reply', name='reply'),
    url(r'^(\d+)/([\w=]+)/(\d+)/(replyall)/$', 'jmail.msg.views.reply', name='replyall'),
)
