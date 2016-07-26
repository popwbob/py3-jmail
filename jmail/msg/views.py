import time

from io import StringIO
from base64 import b64decode
from email.mime.text import MIMEText

from django.http import HttpResponse

from jmail import JMail
from jmail.error import JMailError

from ..mdir import JMailMDir
from . import JMailMessage


def read(req, macct_id, mdir_name_enc, mail_uid, read_html=None):
    try:
        jm = JMail(req, tmpl_name='msg/read', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    jm.log.dbg('Msg read view')
    if read_html is not None:
        read_html = True
    jm.log.dbg('read HTML: ', read_html)
    try:
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(mail_uid, peek=False)
    except JMailError as e:
        return e.response()
    jm.tmpl_data({
        'load_navbar_path': True,
        'mdir': mdir,
        'msg': msg,
        'read_html': read_html,
    })
    jm.log.dbg('Msg read view render')
    return jm.render()


def source(req, macct_id, mdir_name_enc, mail_uid):
    try:
        jm = JMail(req, tmpl_name='msg/source', macct_id=macct_id, imap_start=True)
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(mail_uid, peek=False)
        jm.tmpl_data({
            'load_navbar_path': True,
            'mdir': mdir,
            'msg': msg,
        })
    except JMailError as e:
        return e.response()
    return jm.render()


def attach(req, macct_id, mdir_name_enc, mail_uid, filename_enc):
    try:
        jm = JMail(req, tmpl_name='msg/attach', macct_id=macct_id,
                imap_start=True)
    except JMailError as e:
        return e.response()

    try:
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(mail_uid)
    except JMailError as e:
        return e.response()

    a = None
    for p in msg.parts():
        if p.is_attach():
            if p.filename_encode() == filename_enc:
                a = p

    if a is None:
        return jm.error(404, 'No attach found!')

    resp = HttpResponse(a.payload(), content_type='{}; charset={}'.format(
            a.content_type(), a.get_charset()))

    resp['Content-Disposition'] = 'attachment; filename="{}"'.format(a.filename())

    jm.log.dbg('Msg attach: ', resp['Content-Disposition'])
    jm.end()
    return resp


def compose(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='msg/compose', macct_id=macct_id)
    except JMailError as e:
        return e.response()
    msg_saved = jm.cache_get('compose:save')
    compose_restore = False
    if msg_saved is not None:
        msg = JMailMessage(source=msg_saved.encode())
        compose_restore = True
    else:
        msg = JMailMessage(source=b'')
        msg.headers.set_hdr('From', jm.macct['address'])
    jm.tmpl_data({
        'load_navbar_path': True,
        'msg': msg,
        'compose_restore': compose_restore,
        'msg_quote_body': False,
    })
    return jm.render()


def __compose_discard(jm, macct_id):
    jm.cache_del('compose:save')
    return jm.redirect('msg:compose', macct_id)


def send(req, macct_id):
    # TODO: el mail se deberia guardar en INBOX.Queue primero, después
    #       iniciar el proceso que mande el/los mails que haya en INBOX.Queue
    #       "parecido" a lo que hace claws.
    #       Mientras tanto, lo guardamos en el cache para que no se pierda
    #       si falla el envio y luego compose lo puede "rescatar".
    try:
        jm = JMail(req, macct_id=macct_id)
    except JMailError as e:
        return e.response()
    jm.log.dbg('mail send: ')

    td = jm.tmpl_data({'load_navbar_path': True})

    if req.method != 'POST':
        return jm.error(400, 'bad request', tmpl_data=td)

    req_cmd = req.POST.get('jmail_cmd')
    if req_cmd == 'discard':
        # -- discard composing
        return __compose_discard(jm, macct_id)

    try:
        msg = MIMEText(req.POST.get('mail_body'), _charset='utf-8')
        msg['From'] = req.POST.get('mail_from')
        msg['To'] = req.POST.get('mail_to')
    except Exception as e:
        return jm.error(500, 'could not create email: '+str(e), tmpl_data=td)

    mail_subject = req.POST.get('mail_subject', '')
    if mail_subject != '':
        msg['Subject'] = mail_subject

    mail_cc = req.POST.get('mail_cc', '')
    if mail_cc != '':
        msg['Cc'] = mail_cc

    mail_bcc = req.POST.get('mail_bcc', '')
    if mail_bcc != '':
        msg['Bcc'] = mail_bcc

    msg['Reply-To'] = msg['From']
    msg['Message-ID'] = '<{}.{}@jmail>'.format(time.time(), jm.user)
    msg['Date'] = time.strftime(jm.conf.get('DATE_HEADER_FORMAT'))
    msg['X-Mailer'] = 'jmail v{}'.format(jm.version)

    # -- save email to cache in case the SMTP fails
    jm.cache_set('compose:save', msg.as_string())

    try:
        smtp = jm.smtp_init()
        smtp.send_message(msg)
        smtp.quit()
    except Exception as e:
        jm.log.err('msg send: ', str(e))
        return jm.error(500, 'SMTP error: '+str(e), tmpl_data=td)

    # -- if all was fine, remove the message from the cache
    jm.cache_del('compose:save')

    return jm.message('mail sent!', tmpl_data=jm.tmpl_data({'load_navbar_path': True}))


def __msg_subject_update(subcmd, subject_orig):
    if subcmd.startswith('reply'):
        if not subject_orig.lower().startswith('re:'):
            return 'Re: '+subject_orig
    elif subcmd == 'forward':
        if not subject_orig.lower().startswith('fw:'):
            return 'Fw: '+subject_orig
    return subject_orig


def reply(req, macct_id, mdir_name_enc, msg_uid, subcmd='reply'):
    try:
        jm = JMail(req, tmpl_name='msg/compose', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    try:
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(msg_uid, peek=False)
    except JMailError as e:
        return e.response()
    # -- set From
    from_orig = msg.headers.get('from')
    msg.headers.set_hdr('from', jm.macct['address'])
    # -- set To
    reply_to_orig = msg.headers.get('reply_to', None)
    if reply_to_orig is None:
        jm.log.dbg('reply using header: To')
    else:
        from_orig = reply_to_orig
        jm.log.dbg('reply using header: Reply-To')
    if subcmd == 'forward':
        msg.headers.set_hdr('to', '')
    else:
        msg.headers.set_hdr('to', from_orig)
    # -- remove CC if not replyall
    if subcmd == 'reply':
        msg.headers.set_hdr('cc', '')
    # -- update subject
    subject_new = __msg_subject_update(subcmd, msg.headers.get('subject', ''))
    msg.headers.set_hdr('subject', subject_new)
    jm.tmpl_data({
        'load_navbar_path': True,
        'msg': msg,
        'mdir': mdir,
        'msg_quote_body': True,
        'msg_date_orig': msg.headers.get('date', '(no date)'),
        'msg_from_orig': from_orig,
    })
    return jm.render()
