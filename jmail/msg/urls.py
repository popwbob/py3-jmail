from django.conf.urls import url
from jmail.msg import views

urlpatterns = [
    url(r'^(\d+)/([\w=]+)/(\d+)/source/$', views.source, name='source'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/$', views.read, name='read'),
    url(r'^(\d+)/([\w=]+)/(\d+)/read/(html)/$', views.read, name='read_html'),

    url(r'^(\d+)/([\w=]+)/(\d+)/attach/([\w=]+)/$', views.attach, name='attach'),

    url(r'^(\d+)/compose/$', views.compose, name='compose'),
    url(r'^(\d+)/send/$', views.send, name='send'),

    url(r'^(\d+)/([\w=]+)/(\d+)/reply/$', views.reply, name='reply'),
    url(r'^(\d+)/([\w=]+)/(\d+)/(replyall)/$', views.reply, name='reply'),
    url(r'^(\d+)/([\w=]+)/(\d+)/(forward)/$', views.reply, name='reply'),
]
