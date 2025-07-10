from django.test import TestCase

from apps.lib.models import Asset
from apps.lib.tasks import check_asset_associations
from apps.lib.test_resources import EnsurePlansMixin
from apps.lib.tests.factories import AssetFactory
from apps.profiles.tests.factories import SubmissionFactory


class TestCheckAssociations(EnsurePlansMixin, TestCase):
    def test_removes(self):
        """
        Test that an asset without associations is properly removed.
        """
        asset = AssetFactory.create()
        check_asset_associations(asset.id)
        with self.assertRaises(Asset.DoesNotExist):
            asset.refresh_from_db()

    def test_preserves(self):
        """
        If a model references this file, it should not remain.
        """
        submission = SubmissionFactory.create()
        check_asset_associations(submission.file.id)
        # Should not raise.
        submission.file.refresh_from_db()

    def test_deletes_files(self):
        raise NotImplementedError()

    def test_deletes_thumbnails(self):
        raise NotImplementedError()
