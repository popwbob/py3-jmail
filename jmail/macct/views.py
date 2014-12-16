import re

from jmail import JMail
from jmail.error import JMailError

from django.forms.models import modelformset_factory

from .models import JMailMAcct, JMailMAcctForm
from . import imap_connect, imap_end


def _get_macct(macct_id):
    try:
        macct = JMailMAcct.objects.filter(pk=macct_id).values()[0]
    except JMailMAcct.DoesNotExist:
        return None
    return macct


def check(req, macct_id, mbox_name):
    try:
        jm = JMail(req, tmpl_name='macct/check')
    except JMailError as e:
        return e.response()

    macct = _get_macct(macct_id)
    jm.log.dbg('macct: ', macct)
    if macct is None:
        return jm.error(400, 'Bad mail account')

    imap = imap_connect(macct)
    try:
        imap.select(mbox_name)
        typ, msgs_ids = imap.search('UTF8', 'ALL')
        jm.log.dbg('typ: ', typ)
        jm.log.dbg('msgs_ids: ', msgs_ids)
    except Exception as e:
        return jm.error(404, 'Mailbox not found: {}'.format(mbox_name))

    showh_re = re.compile(r'^Delivered-To:|^Date:|^From:|^To:|^Subject:|^Message-ID:')
    #~ showh_re = re.compile(r'.*')

    msgs = list()
    for mid in msgs_ids[0].split():
        if mid != b'':
            typ, data = imap.fetch(mid, '(UID FLAGS BODY[HEADER])')
            jm.log.dbg('msg typ: ', typ)
            jm.log.dbg('msg data: ', data)
            headers = data[0][1].splitlines()
            jm.log.dbg('msg headers: ', headers)
            showh = list()
            for hdr in headers:
                if showh_re.match(hdr.decode()):
                    showh.append(hdr)
            if len(showh) > 0:
                msgs.append(showh)

    imap.close()
    imap_end(imap)

    if len(msgs) == 0:
        msgs.append(['NO MESSAGES'])
    jm.tmpl_data({
        'macct': macct,
        'mbox_name': mbox_name,
        'msgs': msgs,
    })
    return jm.render()


def remove(req, macct_id):
    try:
        jm = JMail(req)
    except JMailError as e:
        return e.response()

    macct = _get_macct(macct_id)
    jm.log.dbg('macct: ', macct)
    if macct is None:
        return jm.error(400, 'Bad mail account')
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
    except JMailError as e:
        return e.response()

    macct = _get_macct(macct_id)
    jm.log.dbg('macct: ', macct)
    if macct is None:
        return jm.error(400, 'Bad mail account')
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
    except JMailError as e:
        return e.response()

    macct = _get_macct(macct_id)
    jm.log.dbg('macct: ', macct)
    if macct is None:
        return jm.error(400, 'Bad mail account')

    imap = imap_connect(macct)
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
    imap_end(imap)

    jm.tmpl_data({
        'macct': macct,
        'subs_list': subs_list,
    })
    return jm.render()
