from apps.lib.test_resources import BaseWebAppTest
from apps.profiles.tests.bok_choy.pages import HomePage, CharacterPage
from apps.profiles.tests.factories import CharacterFactory, ImageAssetFactory


class TestHomePage(BaseWebAppTest):

    def test_basic(self):
        HomePage(self.browser).visit()


class TestCharacterPage(BaseWebAppTest):
    def setUp(self):
        super().setUp()
        self.character = CharacterFactory.create()

    def test_basic(self):
        CharacterPage(self.browser, character=self.character).visit()


class TestSubmissionPage(BaseWebAppTest):
    def setUp(self):
        super().setUp()
        self.submission = ImageAssetFactory.create()

    def test_basic(self):
        pass
