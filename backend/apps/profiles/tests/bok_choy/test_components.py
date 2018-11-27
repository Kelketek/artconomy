from apps.lib.test_resources import BaseWebAppTest
from apps.profiles.tests.bok_choy.pages import HomePage, CharacterPage, SubmissionPage, SettingsPage
from apps.profiles.tests.factories import CharacterFactory, ImageAssetFactory, UserFactory


class TestHomePage(BaseWebAppTest):

    def test_basic(self):
        HomePage(self.browser).visit()
        import time
        time.sleep(30)


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
        SubmissionPage(self.browser, submission=self.submission).visit()


class TestSettingsPage(BaseWebAppTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.login(self.user)

    def test_basic(self):
        SettingsPage(self.browser, user=self.user).visit()

    def test_change_settings(self):
        settings = SettingsPage(self.browser, user=self.user)
        settings.visit()
        self.assertFalse(settings.commissions_closed)
        settings.toggle_commissions_closed()
        self.assertTrue(settings.commissions_closed)
        settings.save_settings()
        settings.visit()
        self.assertTrue(settings.commissions_closed)
