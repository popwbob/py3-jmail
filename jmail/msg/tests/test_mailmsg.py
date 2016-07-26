from io import StringIO
from jmail.tests import JMailTest
from jmail.msg import JMailMessage
from jmail.log import JMailLog
from jmail import JMailBase
from django.conf import settings

class TestMailMsg(JMailTest):

    def setUp(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())

    def test_mailmsg(self):
        d = '''X-Test: jmail
Subject: En el =?unknown-8bit?q?R=EDo?=
Mime-Version: 1.0
Content-Type: multipart/alternative; boundary="----=_Part1"

------=_Part1
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

Que direcci=F3n?
'''
        m = JMailMessage(source=d.encode())
        subj = m.headers.get('Subject')
        self.assertTrue(subj.startswith('En el R'))
        self.assertTrue(subj.endswith('o'))
        self.assertEqual(ord(subj[7]), 65533)
        self.assertListEqual(m.body_lines(), [r'Que dirección?'])

    # this should be always the last one
    def test_zzz_cleanup_message(self):
        JMailBase.conf = None
        JMailBase.log = None
