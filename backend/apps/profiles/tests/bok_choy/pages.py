from apps.lib.test_resources import BaseTestPage


class HomePage(BaseTestPage):
    block_id = 'home-page'


class CharacterPage(BaseTestPage):
    block_id = 'character-profile'

    def __init__(self, *args, **kwargs):
        self.character = kwargs.pop('character')
        super().__init__(*args, **kwargs)

    @property
    def _base_url(self):
        return '/profile/{}/characters/{}/'.format(self.character.user.username, self.character.name)


class SubmissionPage(BaseTestPage):
    block_id = 'submission-section'

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission')
        super().__init__(*args, **kwargs)

    @property
    def _base_url(self):
        return '/submissions/{}/'.format(self.submission.id)


class SettingsPage(BaseTestPage):
    block_id = 'settings-section'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SettingsPage, self).__init__(*args, **kwargs)

    @property
    def _base_url(self):
        return '/profile/{}/settings/'.format(self.user.username)

    @property
    def commissions_closed(self):
        return self.q(css='#field-commissions_closed')[0].is_selected()

    def toggle_commissions_closed(self):
        self.q(css='#field-commissions_closed')[0].find_element_by_xpath('..').click()

    def save_settings(self):
        self.q(css='#save-settings').click()
        self.wait_for_element_visibility('#saved-settings-checkmark', 'Checkmark visible')
