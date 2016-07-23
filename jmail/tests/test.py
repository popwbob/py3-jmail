import time
from . import JMailTest
from jmail import JMailBase, JMail

class TestJMail(JMailTest):

    def test_bytes2human(self):
        h = JMailBase.bytes2human(8573200)
        self.assertEqual(h, '8.18MB')

    def test_tmpl_data(self):
        JMailBase._tmpl_data = {}
        d = JMailBase.tmpl_data({})
        self.assertIsNone(d['macct'])
        self.assertEqual(d['date_time'],
                time.strftime('%a, %d %b %Y %H:%M:%S %z', time.localtime()))

    #~ def test_jmail(self):
        #~ jm = JMail()
        #~ print(jm)
