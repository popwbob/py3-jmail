# coding: utf-8

from io import StringIO
from django.conf import settings
from jmail import JMailBase
from jmail.log import JMailLog
from jmail.tests import JMailTest
from jmail.msg.parser import JMailMessageHeaders, JMailMessageDistParser

class TestMsg(JMailTest):

    def setUp(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())

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

    def test_parser(self):
        m = JMailMessageDistParser()
        self.assertEqual(m.body, '')
        self.assertEqual(m.body_html, m.body)
        self.assertIsInstance(m.headers, JMailMessageHeaders)
        self.assertListEqual(m.attachs, [])

    def test_message_parse(self):
        m = JMailMessageDistParser()
        m.parse("")
        self.assertEqual(m.body, '')
        self.assertEqual(m.body_html, '[NO HTML CONTENT]')

    def test_message_parse_headers(self):
        m = JMailMessageDistParser()
        m.parse("K1: V1\nK2: V2\nK3: V3\n\n")
        self.assertEqual(m.body, '')
        self.assertEqual(m.body_html, '[NO HTML CONTENT]')
        self.assertIsInstance(m.headers, JMailMessageHeaders)
        self.assertListEqual(m.headers._data,
                [('K1', 'V1'), ('K2', 'V2'), ('K3', 'V3')])

    def test_message_parse_headers_and_body(self):
        m = JMailMessageDistParser()
        m.parse("K1: V1\nK2: V2\nK3: V3\n\nBL1\nBL2\nBL3\nBL4\nBL5\n")
        self.assertEqual(m.body, "BL1\nBL2\nBL3\nBL4\nBL5\n")
        self.assertEqual(m.body_html, '[NO HTML CONTENT]')
        self.assertIsInstance(m.headers, JMailMessageHeaders)
        self.assertListEqual(m.headers._data,
                [('K1', 'V1'), ('K2', 'V2'), ('K3', 'V3')])

    # this should be always the last one
    def test_zzz_cleanup_message(self):
        JMailBase.conf = None
        JMailBase.log = None
