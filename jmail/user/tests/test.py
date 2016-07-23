from jmail.tests import JMailTest
from jmail.user.models import JMailUser

class TestUser(JMailTest):
    fixtures = ['user']

    def test_user(self):
        u = JMailUser.objects.get(django_user=2)
        self.assertIsInstance(u, JMailUser)
        self.assertEqual(str(u), 'jmailuser')
