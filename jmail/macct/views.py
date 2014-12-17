import email

from jmail import JMail
from jmail.error import JMailError

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
            'macct': {
                'formset': JMailMAcctForm().as_p(),
            },
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
        jm = JMail(req, tmpl_name='macct/subs')
        macct = jm.macct_get(macct_id)
        imap = jm.imap_start(macct)
    except JMailError as e:
        if jm:
            jm.end()
        return e.response()

    jm.log.dbg('macct: ', macct)
    imap.select()

    mbox = imap.lsub()
    jm.log.dbg(mbox)

    subs_list = ['INBOX']
    for d in mbox[1]:
        jm.log.dbg('d: ', d)
        child = d.split()[2].decode().replace('"', '')
        jm.log.dbg('child: ', child)
        subs_list.append(child)

    imap.close()
    jm.imap_end(imap)

    jm.tmpl_data({
        'macct': macct,
        'subs_list': subs_list,
    })
    return jm.render()


def check(req, macct_id, mbox_name):
    try:
        jm = JMail(req, tmpl_name='macct/check')
        macct = jm.macct_get(macct_id)
        imap = jm.imap_start(macct)
    except JMailError as e:
        if jm:
            jm.end()
        return e.response()

    jm.log.dbg('macct: ', macct)

    try:
        imap.select(mbox_name)
        typ, msgs_ids = imap.uid('SEARCH', 'ALL')
        jm.log.dbg('typ: ', typ)
        jm.log.dbg('msgs_ids: ', msgs_ids)
    except Exception as e:
        return jm.error(404, 'Mailbox not found: {}'.format(mbox_name))

    showh_list = [
        #~ '_ALL_',
        #~ 'delivered-to',
        #~ 'message-id',
        #~ 'to',
        'date',
        'from',
        'subject',
    ]

    msgs = list()
    for mid in msgs_ids[0].split():
        msg_info = dict()
        if mid != b'':
            #~ typ, data = imap.fetch(mid, '(BODY[HEADER])')
            typ, data = imap.uid('FETCH', mid, '(BODY[HEADER])')
            headers = email.message_from_bytes(data[0][1])
            msg_info['id'] = mid
            showh = dict()
            for hdr in headers:
                if '_ALL_' in showh_list or hdr.lower() in showh_list:
                    showh[hdr] = headers.get(hdr)
            msg_info['headers'] = showh
            msgs.append(msg_info)

    imap.close()
    jm.imap_end(imap)

    jm.log.dbg('msgs: ', msgs)
    jm.log.dbg('msgs number: ', len(msgs))
    jm.tmpl_data({
        'macct': macct,
        'mbox_name': mbox_name,
        'msgs': msgs,
    })
    return jm.render()
