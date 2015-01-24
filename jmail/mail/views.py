from jmail import JMail
from jmail.error import JMailError

from ..mbox import JMailMBox
from . import JMailMessage


def read(req, macct_id, mbox_name_enc, mail_uid, read_html=None):
    try:
        jm = JMail(req, tmpl_name='mail/read', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    if read_html is not None:
        read_html = True
    jm.log.dbg('read HTML: ', read_html)
    try:
        mbox = JMailMBox(mbox_name_enc, name_encoded=True)
        msg = mbox.msg_fetch(mail_uid, read_html=read_html)
    except JMailError as e:
        return e.response()
    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': mbox.tmpl_data(),
        'msg': msg,
        'read_html': read_html,
    })
    return jm.render()


def source(req, macct_id, mbox_name_enc, mail_uid):
    try:
        jm = JMail(req, tmpl_name='mail/source', macct_id=macct_id, imap_start=True)
        mbox = JMailMBox(mbox_name_enc, name_encoded=True)
        msg = mbox.msg_fetch(mail_uid)
    except JMailError as e:
        return e.response()
    except Exception as e:
        return jm.error(500, e)
    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': mbox.tmpl_data(),
        'msg': msg,
    })
    return jm.render()


def attach(req, macct_id, mbox_name_enc, mail_uid, filename_enc):
    try:
        jm = JMail(req, tmpl_name='mail/attach', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    try:
        mbox = JMailMBox(mbox_name_enc, name_encoded=True)
        msg = mbox.msg_fetch(mail_uid)
    except JMailError as e:
        return e.response()
    attach = None
    for ad in msg.attachs:
        ad_filename_enc = ad.get('filename_enc')
        if ad_filename_enc == filename_enc.encode():
            attach = ad
            break
    jm.tmpl_data({
        'mbox': mbox.tmpl_data(),
        'attach': attach,
    })
    return jm.render()
