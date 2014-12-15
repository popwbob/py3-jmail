from jmail import JMail
from jmail.error import JMailError

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout


def login(req):
    try:
        jm = JMail(req, user_auth=False)
    except JMailError as e:
        return e.response()
    if req.user.is_authenticated():
        return jm.redirect('home')
    return jm.render()


def auth(req):
    try:
        jm = JMail(req, user_auth=False)
    except JMailError as e:
        return e.response()

    if not req.method == 'POST':
        return jm.error(400, 'Bad request')

    user_email = req.POST.get('jmail_user', None)
    if not user_email:
        return jm.error(400, 'No user')

    user_pass = req.POST.get('jmail_user_pass', None)
    if not user_pass:
        return jm.error(400, 'No user pass')

    user = authenticate(username=user_email, password=user_pass)
    if user is not None:
        if user.is_active:
            django_login(req, user)
            return jm.redirect('home')
        else:
            jm.error(401, 'Disabled user')
    else:
        return jm.error(401, 'Invalid login')

    return jm.render()


def logout(req):
    try:
        jm = JMail(req)
    except JMailError as e:
        return e.response()
    jm.doc_navbar = False
    django_logout(req)
    return jm.render()
