import json

from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.contrib.auth import logout as django_logout

from jmail.log import JMailLog
from jmail.error import JMailError, JMailErrorUserUnauth

from jmail.user.models import JMailUser


class JMailBase:
    log = None
    _req = None
    _tmpl_name = None
    _tmpl_path = None
    _tmpl_data = None
    doc_navbar = False
    user = None

    def __str__(self):
        r = '{\n'
        r += '    tmpl_path: {}\n'.format(self._tmpl_path)
        r += '}\n'
        return r


class JMail(JMailBase):
    def __init__(self, req, user_auth=True, tmpl_name=None):
        JMailBase.log = JMailLog()
        self.log.dbg('start')
        JMailBase._req = req
        if user_auth:
            self._user_auth()
        JMailBase._tmpl_data = self._tmpl_data_init(tmpl_name)

    def end(self):
        if self.user is not None:
            self.user.save()
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
            },
            'user': {
                'name': self._req.user,
            },
        }
        td.update(csrf(self._req))
        return td

    def _user_auth(self):
        if self._req.user.is_authenticated():
            if self._req.user.groups.filter(name='wmail').exists():
                try:
                    self.user, created = JMailUser.objects.get_or_create(django_user=self._req.user)
                except JMailUser.DoesNotExist:
                    django_logout(self._req)
                    raise JMailError(self._req, 401, 'Bad user')
                self.log.dbg('user: ', str(self.user))
                self.doc_navbar = True
            else:
                django_logout(self._req)
                raise JMailError(self._req, 401, 'Bad user group')
        else:
            raise JMailErrorUserUnauth(self._req, 401, 'Unauthenticated user')

    def render(self, tmpl_name=None):
        if tmpl_name is not None:
            self._tmpl_name = tmpl_name
            self._tmpl_path = self._tmpl_path_get()
        self._tmpl_data['doc']['navbar'] = self.doc_navbar
        self.end()
        return render(self._req, self._tmpl_path, self._tmpl_data)

    def tmpl_data(self, data):
        self._tmpl_data.update(data)

    def debug_data(self):
        dd = list()
        dd.append('JMail: {}'.format(str(self)))
        dd.append('')
        #~ dd.append('tmpl_data: {}'.format(json.dumps(self._tmpl_data, indent=4)))
        #~ dd.append('')
        return dd

    def error(self, status, message):
        e = JMailError(self._req, status, message)
        self.end()
        return e.response()

    def redirect(self, location):
        self.end()
        return redirect(location)
