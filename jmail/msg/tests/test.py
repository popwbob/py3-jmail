from io import StringIO
from django.conf import settings
from jmail import JMailBase
from jmail.log import JMailLog
from jmail.tests import JMailTest
from jmail.msg import JMailMessage

class TestMsg(JMailTest):

    def setUp(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())

    def test_message(self):
        m = JMailMessage()
        self.assertIsInstance(repr(m), str)
        self.assertIsNone(m.headers)
        self.assertIsInstance(m.flags, tuple)
        self.assertEqual(str(m), '(.headers=None)')

    def test_message_flags(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS ())')
        self.assertIsNone(m.headers)
        self.assertTupleEqual(m.flags, tuple())
        self.assertIsNone(m.seen)

    def test_message_flags_seen(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS (\\Seen))')
        self.assertIsNone(m.headers)
        self.assertTupleEqual(m.flags, (b'\\Seen',))
        self.assertTrue(m.seen)

    def test_message_flags_other(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS (\\Other \\Flags))')
        self.assertIsNone(m.headers)
        self.assertTupleEqual(m.flags, (b'\\Other', b'\\Flags'))
        self.assertFalse(m.seen)

    def test_message_flags_short(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS ())')
        self.assertIsInstance(m.flags_short, str)
        self.assertEqual(m.flags_short, '')

    def test_message_flags_short_attach(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS ())')
        m.attachs = ['fake1', 'fake2']
        s = m._flags_short(m.flags)
        self.assertEqual(s, 'A')

    def test_message_flags_short_answered(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS (\\Answered))')
        self.assertEqual(m.flags_short, 'R')

    def test_zzz_cleanup_message(self):
        """this should be always the last one"""
        JMailBase.conf = None
        JMailBase.log = None
