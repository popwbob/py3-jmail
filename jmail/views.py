from jmail import JMail
from jmail import settings as jmail_settings
from jmail.error import JMailError

from django.conf import settings

def debug(req):
    jm = JMail(req, user_auth=False)
    ddata = jm.debug_data()

    ddata.append('req.path: {}'.format(req.path))
    ddata.append('req.path_info: {}'.format(req.path_info))
    ddata.append('req.encoding: {}'.format(req.encoding))
    ddata.append('req.scheme: {}'.format(req.scheme))
    ddata.append('')

    ddata.append('req.user: {}'.format(type(req.user)))
    ddata.append('req.user: {}'.format(sorted(dir(req.user))))
    ddata.append('req.user: {}'.format(req.user))
    ddata.append('req.user.is_authenticated: {}'.format(req.user.is_authenticated()))
    ddata.append('req.user.groups: {}'.format(type(req.user.groups)))
    ddata.append('')

    ddata.append('req.session: {}'.format(req.session))
    ddata.append('req.session: {}'.format(sorted(dir(req.session))))
    ddata.append('req.session.items: {}'.format(sorted(req.session.items())))
    ddata.append('')

    ddata.append('dir(req): {}'.format(sorted(dir(req))))
    ddata.append('req: {}'.format(req))
    ddata.append('')

    ddata.append('jmail settings: {}'.format(type(jmail_settings)))
    ddata.append('')
    for sn in sorted(dir(jmail_settings)):
        if not sn.startswith('_'):
            ddata.append('{}={}'.format(sn, str(getattr(jmail_settings, sn, None)).strip()))
    ddata.append('')

    ddata.append('django settings: {}'.format(type(settings)))
    ddata.append('')
    for sn in sorted(dir(settings)):
        if not sn.startswith('_'):
            ddata.append('{}={}'.format(sn, str(getattr(settings, sn, None)).strip()))
    ddata.append('')

    jm.tmpl_data({
        'debug': {
            'data': ddata,
        },
    })
    return jm.render()


def home(req):
    from jmail.macct.models import JMailMAcct
    try:
        jm = JMail(req)
    except JMailError as e:
        return e.response()
    try:
        accounts = JMailMAcct.objects.filter(user=jm.user).values()
    except JMailMAcct.DoesNotExist:
        accounts = []
    jm.log.dbg('accounts: ', accounts)
    jm.tmpl_data({
        'mail': {
            'accounts': accounts,
        },
    })
    return jm.render()
