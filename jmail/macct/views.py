import email

from jmail import JMail
from jmail.error import JMailError

from django.forms.models import modelformset_factory

from .models import JMailMAcct, JMailMAcctForm


def remove(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='macct/remove')
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
        jm = JMail(req, tmpl_name='macct/create')
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
