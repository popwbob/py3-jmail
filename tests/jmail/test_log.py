from io import StringIO
from .. import JMailTest
from jmail.log import JMailLog

class TestJMailLog(JMailTest):

    def setUp(self):
        self.log = JMailLog()
        self.log._outfile = StringIO()

    def test_log_dbg(self):
        self.log.dbg("fake msg")
        self.log._outfile.seek(0, 0)
        self.assertEqual(self.log._outfile.read().strip(), 'JMail[DGB] - fake msg')

    def test_log_err(self):
        self.log.err("fake msg")
        self.log._outfile.seek(0, 0)
        self.assertEqual(self.log._outfile.read().strip(), 'JMail[ERR] - fake msg')

    def test_log_warn(self):
        self.log.warn("fake msg")
        self.log._outfile.seek(0, 0)
        self.assertEqual(self.log._outfile.read().strip(), 'JMail[WRN] - fake msg')
