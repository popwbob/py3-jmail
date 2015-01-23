from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'jmail.user.views.home', name='home'),
    url(r'^login/$', 'jmail.user.views.login', name='login'),
    url(r'^auth/$', 'jmail.user.views.auth', name='auth'),
    url(r'^logout/$', 'jmail.user.views.logout', name='logout'),
)
