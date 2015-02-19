from .. import JMail, JMailError
from ..mdir import JMailMDir


def subs(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='mdir/subs', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    try:
        mdir = JMailMDir(name='INBOX')
    except JMailError as e:
        return e.response()
    subs_list = mdir.subs_list()
    jm.tmpl_data({
        'load_navbar_path': True,
        'subs_list': subs_list,
    })
    return jm.render()


def check(req, macct_id, mdir_name_enc):
    try:
        jm = JMail(req, tmpl_name='mdir/check', macct_id=macct_id, imap_start=True)
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msgs = mdir.msg_getlist()
    except JMailError as e:
        return e.response()
    #~ except Exception as e:
        #~ return jm.error(500, e)
    jm.tmpl_data({
        'load_navbar_path': True,
        'mdir': mdir,
        'msgs': msgs,
    })
    return jm.render()
