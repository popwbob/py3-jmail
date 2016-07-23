from .. import JMailTest
from jmail import error

class TestJMailError(JMailTest):

    def test_message_page(self):
        m = error.JMailMessagePage("fake msg")
        self.assertEqual(str(m), "200 fake msg")

    def test_message_page_tmpl_data(self):
        m = error.JMailMessagePage("fake msg")
        d = m._tmpl_data()
        self.assertDictEqual(d['doc'],  {
            'error': False, 'message': 'fake msg',
            'status': 200, 'title': 'JMail'})
