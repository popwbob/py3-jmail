from io import StringIO
from jmail.tests import JMailTest
from jmail.msg import JMailMessage
from jmail.log import JMailLog
from jmail import JMailBase
from django.conf import settings

eml1 = '''X-Test: jmail
Subject: Hola

Mundo!
'''.encode()


eml_mpart = '''X-Test: jmail
Subject: En el =?unknown-8bit?q?R=EDo?=
Mime-Version: 1.0
Content-Type: multipart/alternative; boundary="----=_Part"

------=_Part
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

Que direcci=F3n?
------=_Part--
'''.encode()


eml_mpart_html = '''X-Test: jmail
Subject: html email
Mime-Version: 1.0
Content-Type: multipart/alternative; boundary="----=_Part"

------=_Part
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

plain text body
------=_Part
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

<body>html</body>
------=_Part--
'''.encode()


eml_mpart_attach = '''X-Test: jmail
Subject: html email
Mime-Version: 1.0
Content-Type: multipart/alternative; boundary="----=_Part"

------=_Part
Content-Type: text/plain; charset=US-ASCII
Content-Transfer-Encoding: 7bit
Content-Disposition: inline

plain text body
------=_Part
Content-Type: application/octet-stream
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=jmail-attach.test

aG9sYSBtdW5kbyEK
------=_Part
Content-Type: application/octet-stream
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=jmail-attach.ignored

aG9sYSBtdW5kbyEK
------=_Part--
'''.encode()


class TestMailMsg(JMailTest):

    def setUp(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())

    def test_mailmsg(self):
        m = JMailMessage(source=eml1)
        self.assertEqual(m.headers.get('X-Test'), 'jmail')
        self.assertEqual(m.headers.get('Subject'), 'Hola')
        self.assertEqual(m.payload(), b'Mundo!\n')
        self.assertEqual(m.size_human(), '36.00B')

    def test_mailmsg_source(self):
        m = JMailMessage(source=eml_mpart)
        sl = m.source_lines()
        self.assertEqual(len(sl), 11)
        self.assertEqual(sl[0], 'X-Test: jmail')
        self.assertEqual(sl[1], 'Subject: En el =?unknown-8bit?q?R=EDo?=')
        self.assertEqual(sl[9], 'Que direcci=F3n?')
        self.assertEqual(sl[10], '------=_Part--')

    def test_mailmsg_mpart(self):
        m = JMailMessage(source=eml_mpart)
        subj = m.headers.get('Subject')
        self.assertTrue(subj.startswith('En el R'))
        self.assertTrue(subj.endswith('o'))
        self.assertEqual(ord(subj[7]), 65533)
        self.assertEqual(m.body(), 'Que dirección?')

    def test_mailmsg_mpart_html(self):
        m = JMailMessage(source=eml_mpart_html)
        self.assertEqual(m.body_html(), '<body>html</body>')
        self.assertIsNone(m.payload())

    def test_mailmsg_mpart_attach(self):
        m = JMailMessage(source=eml_mpart_attach)
        self.assertEqual(m.body(), 'plain text body')
        p = m.parts()
        self.assertEqual(len(p), 3)
        self.assertEqual(p[1].payload(), b'hola mundo!\n')
        self.assertEqual(p[1].filename(), 'jmail-attach.test')
        self.assertEqual(p[1].filename_encode(), 'am1haWwtYXR0YWNoLnRlc3Q=')
        self.assertEqual(p[1].size_human(), '150.00B')

    # this should be always the last one
    def test_zzz_cleanup_message(self):
        JMailBase.conf = None
        JMailBase.log = None
