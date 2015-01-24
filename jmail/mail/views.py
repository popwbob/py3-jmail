from base64 import urlsafe_b64decode

from jmail import JMail
from jmail.error import JMailError

from . import JMailMessage


def _mdata_debug(jm, mdata):
    mdata_debug = list()
    if jm.debug:
        mdata_debug.append('mdata: {}'.format(type(mdata)))
        mdata_debug.append('epilogue: {}'.format(mdata.epilogue))
        mdata_debug.append('get_charset(): {}'.format(mdata.get_charset()))
        mdata_debug.append('get_charsets(): {}'.format(mdata.get_charsets()))
        mdata_debug.append('get_content_charset(): {}'.format(mdata.get_content_charset()))
        mdata_debug.append('get_content_maintype(): {}'.format(mdata.get_content_maintype()))
        mdata_debug.append('get_content_subtype(): {}'.format(mdata.get_content_subtype()))
        mdata_debug.append('get_content_type(): {}'.format(mdata.get_content_type()))
        mdata_debug.append('get_default_type(): {}'.format(mdata.get_default_type()))
        mdata_debug.append('get_filename(): {}'.format(mdata.get_filename()))
        #~ mdata_debug.append('get_param(): {}'.format(mdata.get_param()))
        mdata_debug.append('get_params(): {}'.format(mdata.get_params()))
        mdata_debug.append('get_payload(): {}'.format(mdata.get_payload()))
        mdata_debug.append('get_unixfrom(): {}'.format(mdata.get_unixfrom()))
        mdata_debug.append('is_multipart(): {}'.format(mdata.is_multipart()))
        mdata_debug.append('preamble: {}'.format(mdata.preamble))
        mdata_debug.append('')
        for part in mdata.walk():
            mdata_debug.append(part.get_content_type())
    return mdata_debug


def read(req, macct_id, mbox_name_enc, mail_uid, read_html=None):
    try:
        jm = JMail(req, tmpl_name='mail/read', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()

    if read_html is not None:
        read_html = True
    jm.log.dbg('read HTML: ', read_html)

    mbox_name = urlsafe_b64decode(mbox_name_enc.encode())
    msg = JMailMessage(mail_uid.encode(), mbox_name, read_html=read_html)
    msg.fetch()

    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': {
            'name': mbox_name,
            'name_encode': mbox_name_enc,
        },
        'msg': msg,
        'read_html': read_html,
    })
    return jm.render()


def source(req, macct_id, mbox_name_enc, mail_uid):
    try:
        jm = JMail(req, tmpl_name='mail/source', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()

    mbox_name = urlsafe_b64decode(mbox_name_enc.encode())
    try:
        msg = JMailMessage(mail_uid.encode(), mbox_name)
        msg.fetch()
    except Exception as e:
        return jm.error(500, e.args[0])

    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': {
            'name': mbox_name,
            'name_encode': mbox_name_enc,
        },
        'msg': msg,
    })
    return jm.render()
