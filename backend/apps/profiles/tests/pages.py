from bok_choy.javascript import js_defined

from tests.test_resources import BaseTestPage


class Asset(BaseTestPage):
    url = None

    def select(self):
        self.q().click()
        self.wait_for_element_presence(
            '.character-refsheet-container img[src="{}"]'.format(self.src),
            'Asset is displayed.',
            root=True
        )

    @property
    def src(self):
        return self.q(css='img')[0].get_property('src')


class CharBlock(BaseTestPage):
    url = None

    @property
    def name(self):
        return self.q(css=".card-header".format(self.block_id)).text

    @property
    def description(self):
        return self.q(css=".character-description").text

    @property
    def assets(self):
        return [Asset(self.browser, asset.get_attribute('id')) for asset in self.q(css=".character-gallery-image")]

    @property
    def asset_controls(self):
        return self.q(css='.asset-controls')


@js_defined('artconomy.loaded')
class CharacterListPage(BaseTestPage):
    """
    Character listing page.
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CharacterListPage, self).__init__(*args, **kwargs)

    @property
    def _base_url(self):
        return '/profiles/{}/characters/'.format(self.user.username)

    def is_browser_on_page(self):
        return self.q(css="#character-list") and "{}'s characters".format(self.user.username) in self.browser.title

    @property
    def characters(self):
        return [CharBlock(self.browser, char.get_attribute('id')) for char in self.q(css=".character-container")]

    @property
    def new_char_button(self):
        return self.q(css='#new-char-button')