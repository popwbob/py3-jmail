from django.shortcuts import render, redirect


class JMailError(Exception):
    status = None
    message = None
    req = None

    def __init__(self, status, message):
        from . import JMailBase
        self.status = status
        self.message = message
        self.req = JMailBase._req

    def tmpl_data(self):
        td = {
            'doc': {
                'error': True,
                'title': 'JMail Error - {}'.format(str(self.status)),
            },
            'error': {
                'status': self.status,
                'message': self.message,
            },
        }
        return td

    def response(self):
        return render(self.req, 'error.html', self.tmpl_data(), status=self.status)


class JMailErrorUserUnauth(JMailError):
    def response(self):
        return redirect('user:login')
