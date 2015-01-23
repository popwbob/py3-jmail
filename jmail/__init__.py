import json
import imaplib

from base64 import urlsafe_b64encode

from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.contrib.auth import logout as django_logout
from django.conf import settings

from jmail.log import JMailLog
from jmail.error import JMailError, JMailErrorUserUnauth

from jmail.user.models import JMailUser
from jmail.macct.models import JMailMAcct

IMAP_DEBUG = 3


class JMailBase:
    log = None
    _req = None
    _tmpl_name = None
    _tmpl_path = None
    _tmpl_data = None
    imap = None
    doc_navbar = False
    user = None
    debug = None
    macct = None
    charset = 'utf-8'

    def __str__(self):
        r = '{\n'
        r += '    tmpl_path: {}\n'.format(self._tmpl_path)
        r += '}\n'
        return r


class JMail(JMailBase):

    def __init__(self, req, user_auth=True, tmpl_name=None, macct_id=None, imap_start=False):
        JMailBase.log = JMailLog()
        self.log.dbg('start')
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
        # -- IMAP
        if imap_start:
            self.imap_start(self.macct)


    def _load_settings(self):
        self.debug = settings.DEBUG


    def end(self):
        if self.user is not None:
            self.user.save()
        JMailBase.macct = None
        JMailBase.imap = None
        self.log.dbg('end')


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
            'doc': {
                'error': False,
                'title': 'JMail - {}'.format(self._req.path),
                'navbar': self.doc_navbar,
                'charset': self.charset,
            },
        }
        if self.user is None:
            td.update({'user': None})
        else:
            td.update({
                'user': {
                    'name': self._req.user
                }
            })
        td.update(csrf(self._req))
        return td


    def _user_auth(self):
        if self._req.user.is_authenticated():
            if self._req.user.groups.filter(name='wmail').exists():
                try:
                    self.user, created = JMailUser.objects.get_or_create(django_user=self._req.user)
                except JMailUser.DoesNotExist:
                    django_logout(self._req)
                    raise JMailError(401, 'Bad user')
                self.log.dbg('user: ', str(self.user))
                self.doc_navbar = True
            else:
                django_logout(self._req)
                raise JMailError(401, 'Bad user group')
        else:
            raise JMailErrorUserUnauth(401, 'Unauthenticated user')


    def render(self, tmpl_name=None):
        if tmpl_name is not None:
            self._tmpl_name = tmpl_name
            self._tmpl_path = self._tmpl_path_get()
        self._tmpl_data['doc']['navbar'] = self.doc_navbar
        self.end()
        return render(self._req, self._tmpl_path, self._tmpl_data)


    def tmpl_data(self, data):
        self.log.dbg('tmpl_data macct: ', self.macct)
        self._tmpl_data.update({'macct': self.macct})
        self._tmpl_data.update(data)


    def debug_data(self):
        dd = list()
        dd.append('JMail: {}'.format(str(self)))
        dd.append('')
        #~ dd.append('tmpl_data: {}'.format(json.dumps(self._tmpl_data, indent=4)))
        #~ dd.append('')
        return dd


    def error(self, status, message):
        e = JMailError(status, message)
        self.end()
        return e.response()


    def redirect(self, location):
        self.end()
        return redirect(location)


    def macct_get(self, macct_id):
        self.log.dbg('macct_id: ', macct_id)
        try:
            macct = JMailMAcct.objects.filter(pk=macct_id, user=self.user).values()[0]
        except IndexError:
            raise JMailError(400, 'Invalid mail account')
        except JMailMAcct.DoesNotExist:
            raise JMailError(404, 'Mail account not found')
        if macct is None:
            raise JMailError(400, 'Bad mail account')
        #~ self.log.dbg('macct: ', macct)
        return macct


    def macct_get_all(self):
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
            if e.args[0].startswith(b'[AUTHENTICATIONFAILED]'):
                raise JMailError(401, 'IMAP Authentication failed')
            else:
                raise JMailError(500, e.args[0].decode())


    def imap_end(self, imap=None):
        if imap is None:
            imap = self.imap
        return imap.logout()


    def imap_lsub(self, imap=None):
        if imap is None:
            imap = self.imap
        mbox = imap.lsub()
        self.log.dbg(mbox)
        sl = []
        for d in mbox[1]:
            if d != b'':
                if type(d) == type(tuple()):
                    child = d[1]
                else:
                    child = b' '.join(d.split(b' ')[2:])
                sl.append(child)
        sl.insert(0, b'INBOX')
        self.log.dbg('subs: ', sl)
        #~ sl = sorted(sl)
        r = list()
        for c in sl:
            show_name = c
            if show_name.startswith(b'"'):
                show_name = show_name[1:]
            if show_name.endswith(b'"'):
                show_name = show_name[:-1]
            r.append({
                'name': show_name,
                'imap_name': c.decode(),
                'name_encode': urlsafe_b64encode(c).decode(),
            })
        return r
