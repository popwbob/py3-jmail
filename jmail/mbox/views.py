from .. import JMail, JMailError
from . import JMailMBox


def subs(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='mbox/subs', macct_id=macct_id)
    except JMailError as e:
        return e.response()

    subs_list = jm.cache_get('subs_list', None)
    if subs_list is None:
        try:
            jm.imap_start(jm.macct)
        except JMailError as e:
            return e.response()

        jm.imap.select()
        subs_list = jm.imap_lsub()
        jm.cache_set('subs_list', subs_list, 60)

        jm.imap.close()
        jm.imap_end()

    jm.tmpl_data({
        'load_navbar_path': True,
        'subs_list': subs_list,
    })
    return jm.render()


def check(req, macct_id, mbox_name_enc):
    try:
        jm = JMail(req, tmpl_name='mbox/check', macct_id=macct_id, imap_start=True)
        mbox = JMailMBox(mbox_name_enc, name_encoded=True)
        msgs = mbox.messages(headers_only=True)
    except JMailError as e:
        return e.response()
    #~ except Exception as e:
        #~ return jm.error(500, e)
    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': mbox.tmpl_data(),
        'msgs': msgs,
    })
    return jm.render()
