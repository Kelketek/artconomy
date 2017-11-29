from ddt import ddt, data

from apps.profiles.tests.factories import UserFactory
from apps.profiles.tests.helpers import gen_characters
from apps.profiles.tests.pages import CharacterListPage
from tests.test_resources import BaseWebAppTest


@ddt
class TestCharacterList(BaseWebAppTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.staffer = UserFactory.create(is_staff=True)
        self.characters = gen_characters(self.user, count=2)

    @data('user', 'staffer')
    def test_character_list(self, user=None):
        self.login(getattr(self, user))
        list_page = CharacterListPage(self.browser, user=self.user)
        list_page.visit()
        self.assertEqual(len(list_page.characters), 2)
        for char in list_page.characters:
            self.assertEqual(len(char.assets), 3)
            for asset in char.assets:
                asset.select()
                self.assertTrue(char.asset_controls.visible)
        self.assertTrue(list_page.new_char_button.present)

    @data(True, False)
    def test_character_list_unprivileged(self, logged_in=False):
        if logged_in:
            self.login(self.user2)
        list_page = CharacterListPage(self.browser, user=self.user)
        list_page.visit()
        self.assertEqual(len(list_page.characters), 2)
        for char in list_page.characters:
            self.assertEqual(len(char.assets), 3)
            for asset in char.assets:
                asset.select()
                self.assertFalse(char.asset_controls.visible)
        self.assertFalse(list_page.new_char_button.present)
