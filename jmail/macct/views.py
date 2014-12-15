from jmail import JMail
from jmail.error import JMailError

from .models import JMailMAcct

def check(req, macct_id):
    try:
        jm = JMail(req, tmpl_name='macct/check')
    except JMailError as e:
        return e.response()
    try:
        macct = JMailMAcct.objects.filter(pk=macct_id).values()[0]
        jm.log.dbg('macct: ', macct)
    except JMailMAcct.DoesNotExist:
        return jm.error(400, 'Bad mail account')
    jm.tmpl_data({'macct': macct})
    return jm.render()
