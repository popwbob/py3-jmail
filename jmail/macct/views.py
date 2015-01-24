import email

from base64 import urlsafe_b64decode

from jmail import JMail
from jmail.error import JMailError
from jmail.mail import JMailMessage

from django.forms.models import modelformset_factory

from .models import JMailMAcct, JMailMAcctForm


def remove(req, macct_id):
    try:
        jm = JMail(req)
        macct = jm.macct_get(macct_id)
    except JMailError as e:
        if jm:
            jm.end()
        return e.response()

    jm.log.dbg('macct: ', macct)
    jm.tmpl_data({'macct': macct})

    if req.method == 'POST':
        try:
            dbobj = JMailMAcct.objects.get(pk=macct_id)
            dbobj.delete()
        except Exception as e:
            return jm.error(500, str(e))
        return jm.render(tmpl_name='macct/removed')
    else:
        return jm.render(tmpl_name='macct/remove_confirm')


def create(req):
    try:
        jm = JMail(req)
    except JMailError as e:
        return e.response()

    if req.method == 'POST':
        try:
            macct = JMailMAcct(user=jm.user)
            form = JMailMAcctForm(req.POST, instance=macct)
            jm.log.dbg(sorted(dir(form)))
            jm.log.dbg(form.fields)
            form.save()
        except Exception as e:
            jm.log.err(e)
            return jm.error(500, str(e))
        return jm.redirect('home')
    else:
        jm.tmpl_data({
            'form_data': JMailMAcctForm().as_p(),
        })
        return jm.render()


def edit(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='macct/edit')
        macct = jm.macct_get(macct_id)
    except JMailError as e:
        if jm:
            jm.end()
        return e.response()

    jm.log.dbg('macct: ', macct)
    dbobj = JMailMAcct.objects.get(pk=macct_id)

    if req.method == 'POST':
        try:
            form = JMailMAcctForm(req.POST, instance=dbobj)
            form.save()
            return jm.redirect('home')
        except Exception as e:
            return jm.error(500, str(e))
    else:
        jm.tmpl_data({
            'macct': macct,
            'macct_formset': JMailMAcctForm(instance=dbobj).as_p(),
        })
        return jm.render()


def subs(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='macct/subs', macct_id=macct_id)
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
        jm = JMail(req, tmpl_name='macct/check', macct_id=macct_id, imap_start=True)
    except JMailError as e:
        return e.response()

    jm.log.dbg('mbox_name_enc: ', mbox_name_enc)
    mbox_name = urlsafe_b64decode(mbox_name_enc.encode())
    jm.log.dbg('mbox_name: ', mbox_name)

    # -- get messages uid list
    try:
        jm.imap.select(mbox_name)
        typ, msgs_ids = jm.imap.uid('SEARCH', 'ALL')
        jm.log.dbg('msgs_ids: ', msgs_ids)
        jm.imap.close()
    except Exception as e:
        jm.log.err(e)
        return jm.error(404, 'Mailbox not found: {}'.format(mbox_name))

    # -- get messages headers
    msgs = list()
    for muid in msgs_ids[0].split():
        if muid != b'':
            msg = JMailMessage(muid, mbox_name, headers_only=True)
            msg.fetch()
            msgs.append(msg)

    jm.log.dbg('msgs: ', msgs)
    jm.log.dbg('msgs number: ', len(msgs))
    jm.tmpl_data({
        'load_navbar_path': True,
        'mbox': {
            'name': mbox_name,
            'name_encode': mbox_name_enc,
        },
        'msgs': msgs,
    })
    return jm.render()


def admin(req):
    try:
        jm = JMail(req, tmpl_name='macct/admin')
    except JMailError as e:
        return e.response()
    jm.tmpl_data({
        'mail': {
            'accounts': jm.macct_get_all(),
        },
    })
    return jm.render()
