import smtplib
import time

from base64 import b64decode
from email.mime.text import MIMEText

from django.http import HttpResponse

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
    # XXX: Tal vez seteand Content-Disposition como inline ayude a que
    #      lo muestre el server en lugar de bajarlo?
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
    if attach is None:
        return jm.error(500, 'No attach')
    cs = attach['charset']
    if cs is None:
        cs = jm.charset
    ct = attach['content_type']
    #~ maintype = attach['content_maintype']
    #~ subtype = attach['content_subtype']
    #~ if maintype == 'text':
        #~ if subtype == 'x-patch':
            #~ ct = 'text/plain'
    resp = HttpResponse(content_type='{}; charset={}'.format(ct, cs))
    resp['Content-Disposition'] = attach['disposition']
    jm.end()
    return resp


def compose(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='mail/compose', macct_id=macct_id)
    except JMailError as e:
        return e.response()

    msg = {
        'mail_from': jm.macct['address'],
        'mail_to': '',
        'mail_cc': '',
        'mail_bcc': '',
        'mail_subject': '',
        'mail_body': '',
    }

    msg_saved = jm.cache_get('compose:save')
    if msg_saved is not None:
        msg = {
            'mail_from': msg_saved['From'],
            'mail_to': msg_saved['To'],
            'mail_cc': msg_saved['Cc'] or '',
            'mail_bcc': msg_saved['Bcc'] or '',
            'mail_subject': msg_saved['Subject'],
            'mail_body': b64decode(msg_saved.get_payload().encode()),
            'compose_restore': True,
        }

    jm.tmpl_data({
        'load_navbar_path': True,
        'msg': msg,
    })
    return jm.render()


def __compose_discard(jm, macct_id):
    jm.cache_del('compose:save')
    return jm.redirect('mail:compose', macct_id)


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

    jm.log.dbg('POST: ', req.POST)

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
    msg['X-Mailer'] = 'jmail v0.0'

    # -- save email to cache in case the SMTP fails
    jm.cache_set('compose:save', msg)

    try:
        smtp = smtplib.SMTP(jm.macct['smtp_server'], jm.macct['smtp_server_port'])
        smtp.send_message(msg)
        smtp.quit()
    except Exception as e:
        return jm.error(500, 'SMTP error: '+str(e), tmpl_data=td)

    # -- if all was fine, remove the message from the cache
    jm.cache_del('compose:save')

    return jm.message('mail sent!', tmpl_data=jm.tmpl_data({'load_navbar_path': True}))


def reply(req, macct_id, mbox_name_enc, mail_uid, reply_all=False):
    try:
        jm = JMail(req, tmpl_name='mail/reply', macct_id=macct_id)
    except JMailError as e:
        return e.response()
    jm.tmpl_data({
        'load_navbar_path': True,
        #~ 'mbox': mbox.tmpl_data(),
        #~ 'msg': msg,
    })
    return jm.render()
