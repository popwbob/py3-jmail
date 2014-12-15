from jmail import JMail
from jmail.error import JMailError

from django.forms.models import modelformset_factory

from .models import JMailMAcct, JMailMAcctForm


def _get_macct(macct_id):
    try:
        macct = JMailMAcct.objects.filter(pk=macct_id).values()[0]
    except JMailMAcct.DoesNotExist:
        return None
    return macct


def check(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='macct/check')
    except JMailError as e:
        return e.response()

    macct = _get_macct(macct_id)
    jm.log.dbg('macct: ', macct)
    if macct is None:
        return jm.error(400, 'Bad mail account')
    jm.tmpl_data({'macct': macct})

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
