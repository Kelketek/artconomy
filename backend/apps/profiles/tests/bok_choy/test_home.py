from apps.lib.test_resources import BaseWebAppTest
from apps.profiles.tests.bok_choy.pages import HomePage


class TestHomePage(BaseWebAppTest):

    def test_stub(self):
        HomePage(self.browser).visit()
