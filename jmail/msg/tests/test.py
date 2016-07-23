from jmail.tests import JMailTest
from jmail.msg import JMailMessage

class TestMsg(JMailTest):

    def test_message(self):
        m = JMailMessage()
        self.assertIsNone(m.headers)
