from jmail.tests import JMailTest
from jmail.macct.models import JMailMAcct

class TestMdir(JMailTest):
    fixtures = ['macct']

    def test_macct(self):
        a = JMailMAcct.objects.filter(pk=1, user=2).values()[0]
        self.assertIsInstance(a, dict)
        self.assertEqual(a['id'], 1)
        self.assertEqual(a['user_id'], 2)
        self.assertEqual(a['address'], 'jmailuser@jmail.test')
