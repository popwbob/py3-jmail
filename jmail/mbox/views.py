from .. import JMail, JMailError
from . import JMailMBox


def check(req, macct_id, mbox_name_enc):
    try:
        jm = JMail(req, tmpl_name='mbox/check', macct_id=macct_id, imap_start=True)
        mbox = JMailMBox(mbox_name_enc, name_encoded=True)
        msgs = mbox.messages(headers_only=True)
    except JMailError as e:
        return e.response()
    except Exception as e:
        return jm.error(500, e)
    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': mbox.tmpl_data(),
        'msgs': msgs,
    })
    return jm.render()
