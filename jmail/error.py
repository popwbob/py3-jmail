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

    def tmpl_data(self):
        td = {
            'doc': {
                'error': self._error,
                'title': self._title,
                'status': self.status,
                'message': self.message,
            }
        }
        return td

    def response(self, tmpl_data=None):
        if tmpl_data is None:
            td = self.tmpl_data()
        else:
            td = tmpl_data
            td.update(self.tmpl_data())
        return render(self.req, self._tmpl_path, td, status=self.status)


class JMailError(JMailMessagePage):
    def __init__(self, status, message):
        JMailMessagePage.__init__(self, message, status, title='JMail Error', error=True, tmpl_path='error.html')


class JMailErrorUserUnauth(JMailError):
    def response(self):
        return redirect('user:login')
