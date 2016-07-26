import os
import json
import imaplib
import time
import socket
import smtplib

from io import StringIO
from pprint import pprint
from base64 import urlsafe_b64encode

from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.core.cache import cache as django_cache

from jmail.version import VERSION
from jmail.log import JMailLog
from jmail.error import JMailMessagePage, JMailError, JMailErrorUserUnauth

IMAP_DEBUG = 0
B2H_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']


class JMailBase:
    _req = None
    _tmpl_name = None
    _tmpl_path = None
    _tmpl_data = None
    _start_tstamp = None
    log = None
    imap = None
    user = None
    debug = None
    macct = None
    charset = 'utf-8'
    conf = None
    devmode = None
    version = VERSION

    @classmethod
    def bytes2human(self, size_bytes):
        idx = 0
        sh = size_bytes
        while sh > 1024:
            sh = sh / 1024
            idx += 1
        return '{:.2f}{}'.format(sh, B2H_UNITS[idx])

    @classmethod
    def _cache_key(self, key):
        ck = str(self._req.user)
        ck += ':'+str(self.macct.get('id'))
        ck += ':'+key
        self.log.dbg('cache_key: ', ck)
        return ck

    @classmethod
    def cache_get(self, key, default=None):
        ck = self._cache_key(key)
        cv = django_cache.get(ck, None)
        if cv is None:
            return default
        else:
            return cv

    @classmethod
    def cache_set(self, key, val, ttl=None):
        ck = self._cache_key(key)
        if ttl is None:
            django_cache.set(ck, val)
        else:
            django_cache.set(ck, val, ttl)

    @classmethod
    def cache_del(self, key):
        ck = self._cache_key(key)
        django_cache.delete(ck)

    @classmethod
    def tmpl_data(self, data):
        self._tmpl_data.update({
            'date_time': time.strftime('%a, %d %b %Y %H:%M:%S %z', time.localtime()),
            'macct': self.macct,
        })
        self._tmpl_data.update(data)
        return self._tmpl_data

    @classmethod
    def imap_end(self, imap=None):
        if imap is None:
            imap = self.imap
        if imap is not None:
            if imap.state == 'SELECTED':
                imap.close()
            imap.logout()
        self.log.dbg('imap logged out')

    @classmethod
    def end(self):
        # -- imap
        if self.imap:
            self.log.dbg('imap state: ', self.imap.state)
            if self.imap.state != 'LOGOUT':
                try:
                    self.imap_end()
                except Exception as e:
                    self.log.warn('imap_end: ', e)
        # -- user
        if self.user is not None:
            self.user.save()
        # -- run time
        took = time.time() - self._start_tstamp
        self.log.dbg('end - {}s'.format(took))
        return '{:.3f}'.format(took)


class JMail(JMailBase):

    def __init__(self, req, user_auth=True, tmpl_name=None, macct_id=None, imap_start=False):
        JMailBase._start_tstamp = time.time()
        JMailBase.log = JMailLog()
        self.log.dbg('start: v%s' % VERSION)
        self._load_settings()
        JMailBase._req = req
        # -- user auth
        if user_auth:
            self._user_auth()
        self.log.dbg('user: ', self.user)
        # -- tmpl data init
        JMailBase._tmpl_data = self._tmpl_data_init(tmpl_name)
        # -- mail account
        if macct_id is not None:
            JMailBase.macct = self.macct_get(macct_id)
        # -- network/socket timeout
        socket.setdefaulttimeout(self.conf.get('SOCKETLIB_TIMEOUT', 15))
        self.log.dbg('socket timeout: ', socket.getdefaulttimeout())
        # -- IMAP
        if imap_start:
            self.imap_start(self.macct)


    def _load_settings(self):
        JMailBase.debug = settings.DEBUG
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.devmode = os.getenv('JMAIL_DEVMODE', None)


    def _tmpl_path_get(self):
        p = self._req.path
        if self._tmpl_name is not None:
            p = self._tmpl_name
        if p.startswith('/'):
            p = p[1:]
        if p.endswith('/'):
            p = p[:-1]
        if p == '':
            p = 'home'
        return '{}.html'.format(p)


    def _tmpl_data_init(self, tmpl_name):
        JMailBase._tmpl_name = tmpl_name
        JMailBase._tmpl_path = self._tmpl_path_get()
        td = {
            'jmail': {
                'devmode': self.devmode,
                'tmpl_debug': None,
                'version': VERSION,
            },
            'doc': {
                'error': False,
                'title': 'JMail - {}'.format(self._req.path),
                'charset': self.charset,
            },
        }
        if self.user is None:
            td.update({'user': None})
        else:
            td.update({
                'user': {
                    'name': str(self._req.user)
                }
            })
        return td


    def _user_auth(self):
        from jmail.user.models import JMailUser
        if self._req.user.is_authenticated():
            if self._req.user.groups.filter(name='wmail').exists():
                try:
                    self.user, created = JMailUser.objects.get_or_create(django_user=self._req.user)
                except JMailUser.DoesNotExist:
                    django_logout(self._req)
                    raise JMailError(401, 'Bad user')
            else:
                django_logout(self._req)
                raise JMailError(401, 'Bad user group')
        else:
            raise JMailErrorUserUnauth(401, 'Unauthenticated user')


    def render(self, tmpl_name=None, content_type='text/html', charset=None):
        if tmpl_name is not None:
            self._tmpl_name = tmpl_name
            self._tmpl_path = self._tmpl_path_get()
        if charset is None:
            charset = self.charset
        ctype = '{}; charset={}'.format(content_type, charset)
        self._tmpl_data['doc']['charset'] = charset
        if self.devmode:
            self._tmpl_data['jmail']['tmpl_debug'] = self._tmpl_data_debug()
        self._tmpl_data['took'] = self.end()
        self.log.dbg('Render: ', ctype, ' ', self._tmpl_path)
        return render(self._req, self._tmpl_path, self._tmpl_data, content_type=ctype)


    def _tmpl_data_debug(self):
        rs = StringIO()
        pprint(self._tmpl_data, stream=rs)
        rs.seek(0, 0)
        return rs.read()


    def debug_data(self):
        dd = list()
        dd.append('JMail: {}'.format(str(self)))
        dd.append('')
        return dd


    def error(self, status, message, tmpl_data=None):
        e = JMailError(status, message)
        td = dict()
        if tmpl_data is None:
            td = self.tmpl_data({})
        else:
            td.update(tmpl_data)
        td['took'] = self.end()
        return e.response(tmpl_data=td)


    def message(self, message, tmpl_data=None):
        e = JMailMessagePage(message)
        td = dict()
        if tmpl_data is not None:
            td.update(tmpl_data)
        td['took'] = self.end()
        return e.response(tmpl_data=td)


    def redirect(self, *location):
        self.end()
        return redirect(*location)


    def macct_get(self, macct_id):
        from jmail.macct.models import JMailMAcct
        self.log.dbg('macct_id: ', macct_id)
        try:
            macct = JMailMAcct.objects.filter(pk=macct_id, user=self.user).values()[0]
        except IndexError:
            raise JMailError(400, 'Invalid mail account')
        except JMailMAcct.DoesNotExist:
            raise JMailError(404, 'Mail account not found')
        if macct is None:
            raise JMailError(400, 'Bad mail account')
        return macct


    def macct_get_all(self):
        from jmail.macct.models import JMailMAcct
        try:
            accounts = JMailMAcct.objects.filter(user=self.user).values()
        except JMailMAcct.DoesNotExist:
            accounts = []
        self.log.dbg('macct_get_all accounts: ', len(accounts))
        return accounts


    def imap_start(self, macct):
        use_ssl = macct.get('imap_server_ssl')
        try:
            if use_ssl:
                JMailBase.imap = imaplib.IMAP4_SSL(macct.get('imap_server'), macct.get('imap_server_port'))
            else:
                JMailBase.imap = imaplib.IMAP(macct.get('imap_server'), macct.get('imap_server_port'))
            self.imap.debug = IMAP_DEBUG
            self.imap.login(macct.get('address'), macct.get('password', ''))
            self.log.dbg('imap_start: ', self.imap)
            return self.imap
        except Exception as e:
            self.log.err('imap_start: [{}] {}'.format(type(e), str(e)))
            try:
                if e.args[0].startswith(b'[AUTHENTICATIONFAILED]'):
                    raise JMailError(401, 'IMAP Authentication failed')
            except:
                pass
            raise JMailError(500, str(e.args))


    def smtp_init(self):
        s = smtplib.SMTP(self.macct['smtp_server'], self.macct['smtp_server_port'])
        if self.macct['smtp_server_tls']:
            self.log.dbg('smtp starttls')
            s.starttls()
        if self.macct.get('smtp_authenticate', True):
            self.log.dbg('smtp authenticate')
            s.login(self.macct.get('address'), self.macct.get('password', ''))
        return s
