from .. import JMailTest
from jmail import JMailBase

class TestJMail(JMailTest):

    def test_bytes2human(self):
        h = JMailBase.bytes2human(8573200)
        self.assertEqual(h, '8.18MB')
