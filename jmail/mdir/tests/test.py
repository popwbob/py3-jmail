from io import StringIO
from django.conf import settings
from jmail.tests import JMailTest
from jmail.macct.models import JMailMAcct
from jmail.log import JMailLog
from jmail import mdir, JMailBase

class TestMdir(JMailTest):
    fixtures = ['user', 'macct']

    def test_mdir_cache(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())
        JMailBase.macct = JMailMAcct.objects.filter(pk=1, user=2).values()[0]
        c = mdir.JMailMDirCache()
        c.init(b'fake-cache')
        JMailBase.conf = None
        JMailBase.log = None
        JMailBase.macct = None

    def test_mdir_cache_disable(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())
        JMailBase.macct = JMailMAcct.objects.filter(pk=1, user=2).values()[0]
        c = mdir.JMailMDirCache()
        JMailBase.conf['MDIR_CACHE_ENABLE'] = False
        c.init(b'fake-cache')
        JMailBase.conf = None
        JMailBase.log = None
        JMailBase.macct = None
