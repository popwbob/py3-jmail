from django.shortcuts import render, redirect


class JMailMessagePage(Exception):
    _user = None
    _title = None
    _error = None
    _tmpl_path = None
    status = None
    message = None
    req = None

    def __init__(self, message, status=200, title='JMail', error=False, tmpl_path='message.html'):
        from . import JMailBase
        self.status = status
        self.message = message
        self.req = JMailBase._req
        self._user = JMailBase.user
        self._title = title
        self._error = error
        self._tmpl_path = tmpl_path
        self._jm_tmpl_data = JMailBase.tmpl_data
        self._jm_end = JMailBase.end

    def _tmpl_data(self):
        td = self._jm_tmpl_data({
            'doc': {
                'error': self._error,
                'title': self._title,
                'status': self.status,
                'message': self.message,
            }
        })
        return td

    def response(self, tmpl_data=None):
        if tmpl_data is None:
            td = self._tmpl_data()
        else:
            td = tmpl_data
            td.update(self._tmpl_data())
        td['took'] = self._jm_end()
        return render(self.req, self._tmpl_path, td, status=self.status)

    def __str__(self):
        return '{} {}'.format(self.status, self.message)


class JMailError(JMailMessagePage):
    def __init__(self, status, message):
        JMailMessagePage.__init__(self, message, status, title='JMail Error', error=True, tmpl_path='error.html')


class JMailErrorUserUnauth(JMailError):
    def response(self):
        return redirect('user:login')
