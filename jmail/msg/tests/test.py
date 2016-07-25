from io import StringIO
from django.conf import settings
from jmail import JMailBase
from jmail.log import JMailLog
from jmail.tests import JMailTest
from jmail.msg import JMailMessage, JMailMessageHeaders

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

    # -- test message flags

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

    #~ def test_message_flags_short_attach(self):
        #~ m = JMailMessage(meta=b'32 (UID 316 FLAGS ())')
        #~ m.attachs = ['fake1', 'fake2']
        #~ s = m._flags_short(m.flags)
        #~ self.assertEqual(s, 'A')

    def test_message_flags_short_answered(self):
        m = JMailMessage(meta=b'32 (UID 316 FLAGS (\\Answered))')
        self.assertEqual(m.flags_short, 'R')

    # -- test message headers

    def test_message_headers(self):
        h = JMailMessageHeaders()
        self.assertEqual(str(h), '[]')
        self.assertListEqual(h._data, [])
        self.assertDictEqual(h.short(),
                {'to': '', 'date': '', 'subject': '', 'from': ''})

    def test_message_headers_data(self):
        h = JMailMessageHeaders([('HK1', 'HV1'), ('HK2', 'HV2')])
        self.assertListEqual(h._data, [('HK1', 'HV1'), ('HK2', 'HV2')])

    def test_message_headers_data_short(self):
        h = JMailMessageHeaders([('To', 'dest@jmail.test')])
        self.assertDictEqual(h.short(),
                {'to': 'dest@jmail.test', 'date': '', 'subject': '', 'from': ''})

    def test_message_headers_get(self):
        h = JMailMessageHeaders([('HK1', 'HV1'), ('HK2', 'HV2')])
        self.assertEqual(h.get('HK2'), 'HV2')
        self.assertIsInstance(h.get('HK3'), str)
        self.assertIsNone(h.get('HK3', None))
        self.assertEqual(h['HK1'], 'HV1') # __getitem__
        self.assertFalse('HK3' in h) # __contains__

    def test_message_headers_parse_key(self):
        h = JMailMessageHeaders([('H-K1', 'HV1')])
        self.assertEqual(h.get('H_K1'), 'HV1')

    def test_message_headers_get_raw(self):
        h = JMailMessageHeaders([('HK1', '=?UTF-8?B?SmVyZW3DrWFz?=')])
        self.assertEqual(h.get_raw('HK1'), '=?UTF-8?B?SmVyZW3DrWFz?=')

    def test_message_headers_decode(self):
        h = JMailMessageHeaders([('HK1', '=?UTF-8?B?SmVyZW3DrWFz?= Castegl')])
        self.assertEqual(h.get('HK1'), 'Jeremías  Castegl')

    def test_message_headers_len(self):
        h = JMailMessageHeaders([('HK1', ''), ('HK2', '')])
        self.assertEqual(len(h), 2)

    def test_message_set_header(self):
        h = JMailMessageHeaders()
        self.assertEqual(str(h), '[]')
        h.set_hdr('HK1', 'HV1')
        self.assertEqual(str(h), "[('HK1', 'HV1')]")
        # override
        h.set_hdr('HK1', 'HV2')
        self.assertEqual(str(h), "[('HK1', 'HV2')]")

    def test_message_headers_short(self):
        h = JMailMessageHeaders()
        self.assertDictEqual(h.short(),
                {'date': '', 'from': '', 'subject': '', 'to': ''})

    def test_message_headers_short_long_line(self):
        h = JMailMessageHeaders([('To', 'a' * 128)])
        self.assertFalse(h.short()['to'].endswith('..'))
        h = JMailMessageHeaders([('To', 'a' * 129)])
        self.assertTrue(h.short()['to'].endswith('..'))

    def test_message_headers_short_date(self):
        h = JMailMessageHeaders([('Date', 'Fri, 22 Apr 2016 07:34:25 +0000')])
        self.assertEqual(h.short()['date'], '20160422 07:34')

    # -- test message parsing

    def test_message_parse(self):
        m = JMailMessage(source=b'')
        self.assertIsInstance(m.headers, JMailMessageHeaders)
        #~ self.assertEqual(m.body_html, '[NO HTML CONTENT]')

    def test_message_size_human(self):
        m = JMailMessage(source=b'\n\n\n')
        self.assertEqual(m.size_human(), '3.00B')

    def test_message_body_lines(self):
        m = JMailMessage(source=b'Content-Type: text/plain; charset=UTF-8\n\n\n')
        self.assertListEqual(m.body_lines(), [''])

    # -- cleanup

    # this should be always the last one
    def test_zzz_cleanup_message(self):
        JMailBase.conf = None
        JMailBase.log = None
