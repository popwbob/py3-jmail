import smtplib
import time

from io import StringIO
from base64 import b64decode
from email.mime.text import MIMEText

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from jmail import JMail
from jmail.error import JMailError

from ..mdir import JMailMDir
from . import JMailMessage


def read(req, macct_id, mdir_name_enc, mail_uid, read_html=None):
    try:
        jm = JMail(req, tmpl_name='msg/read', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()

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
        'mail_uid': mail_uid,
        'read_html': read_html,
    })
    return jm.render()


def source(req, macct_id, mdir_name_enc, mail_uid):
    try:
        jm = JMail(req, tmpl_name='msg/source', macct_id=macct_id, imap_start=True)
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg_source = mdir.msg_source(mail_uid)
    except JMailError as e:
        return e.response()
    #~ except Exception as e:
        #~ return jm.error(500, e)
    jm.tmpl_data({
        'load_navbar_path': True,
        'mdir': mdir,
        'msg': {
            'uid': mail_uid,
            'source': msg_source,
        },
    })
    return jm.render()


def attach(req, macct_id, mdir_name_enc, mail_uid, filename_enc):
    # XXX: Tal vez seteand Content-Disposition como inline ayude a que
    #      lo muestre el server en lugar de bajarlo?
    try:
        jm = JMail(req, tmpl_name='msg/attach', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()

    try:
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(mail_uid)
    except JMailError as e:
        return e.response()

    attach = None
    for ad in msg.attachs:
        ad_filename_enc = ad.get('filename_encode')
        if ad_filename_enc == filename_enc.encode():
            attach = ad
            break
    if attach is None:
        return jm.error(500, 'No attach')

    resp = HttpResponse(attach['payload'], content_type='{}; charset={}'.format(attach['content_type'], attach['charset']))

    #~ wrapper = FileWrapper(StringIO(attach['payload']))
    #~ resp = HttpResponse(wrapper, content_type='{}; charset={}'.format(attach['content_type'], attach['charset']))

    resp['Content-Disposition'] = attach['content_disposition']
    if attach['content_transfer_encoding'] is not None:
        resp['Content-Transfer-Encoding'] = attach['content_transfer_encoding']
    jm.end()
    return resp


def compose(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='msg/compose', macct_id=macct_id)
    except JMailError as e:
        return e.response()
    msg = JMailMessage()
    msg.headers.set_hdr('From', jm.macct['address'])
    msg_saved = jm.cache_get('compose:save')
    compose_restore = False
    if msg_saved is not None:
        msg = JMailMessage((None, msg_saved))
        compose_restore = True
    jm.tmpl_data({
        'load_navbar_path': True,
        'msg': msg,
        'compose_restore': compose_restore,
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
        smtp = smtplib.SMTP(jm.macct['smtp_server'], jm.macct['smtp_server_port'])
        smtp.send_message(msg)
        smtp.quit()
    except Exception as e:
        return jm.error(500, 'SMTP error: '+str(e), tmpl_data=td)

    # -- if all was fine, remove the message from the cache
    jm.cache_del('compose:save')

    return jm.message('mail sent!', tmpl_data=jm.tmpl_data({'load_navbar_path': True}))


def reply(req, macct_id, mdir_name_enc, msg_uid, reply_all=None):
    try:
        jm = JMail(req, tmpl_name='msg/compose', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()
    try:
        mdir = JMailMDir(name_encode=mdir_name_enc)
        msg = mdir.msg_get(msg_uid, peek=False)
    except JMailError as e:
        return e.response()
    # TODO / FIXME
    # * Salvo que sea un replyall, limpiar CC y BCC
    # -- From
    from_orig = msg.headers.get('from')
    jm.log.dbg('reply from orig: ', from_orig)
    msg.headers.set_hdr('from', jm.macct['address'])
    jm.log.dbg('reply from: ', msg.headers.get('from'))
    # -- To
    to_orig = msg.headers.get('to')
    jm.log.dbg('reply to orig: ', to_orig)
    msg.headers.set_hdr('to', from_orig)
    jm.log.dbg('reply to: ', msg.headers.get('to'))
    jm.tmpl_data({
        'load_navbar_path': True,
        'msg': msg,
    })
    return jm.render()