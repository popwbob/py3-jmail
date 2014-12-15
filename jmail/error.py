from django.shortcuts import render, redirect


class JMailError(Exception):
    status = None
    message = None
    req = None

    def __init__(self, req, status, message):
        self.status = status
        self.message = message
        self.req = req

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
