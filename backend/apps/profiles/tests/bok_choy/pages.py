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
