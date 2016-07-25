# coding: utf-8

from io import StringIO
from django.conf import settings
from jmail import JMailBase
from jmail.log import JMailLog
from jmail.tests import JMailTest
from jmail.msg.parser import JMailMessageDistParser

class TestMsg(JMailTest):

    def setUp(self):
        JMailBase.conf = settings.JMAIL.copy()
        JMailBase.log = JMailLog(outfile=StringIO())

    def test_parser(self):
        m = JMailMessageDistParser()
        self.assertEqual(m.body_html, '')
        self.assertListEqual(m.attachs, [])

    # this should be always the last one
    def test_zzz_cleanup_message(self):
        JMailBase.conf = None
        JMailBase.log = None
