from unittest import TestCase

import ddt

from apps.profiles.social_matchers import link_to_social
from apps.profiles.tests.fixtures import LINK_TO_SOCIAL_SCENARIOS


@ddt.ddt
class TestSocialMatchers(TestCase):
    @ddt.data(*LINK_TO_SOCIAL_SCENARIOS)
    @ddt.unpack
    def test_link_to_social_spec(self, link, spec):
        self.assertEqual(link_to_social(link), spec)
