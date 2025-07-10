from unittest.mock import patch

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
        check_asset_associations(asset.id, force=True)
        with self.assertRaises(Asset.DoesNotExist):
            asset.refresh_from_db()

    def test_preserves(self):
        """
        If a model references this file, it should not remain.
        """
        submission = SubmissionFactory.create()
        check_asset_associations(submission.file.id, force=True)
        # Should not raise.
        submission.file.refresh_from_db()

    def test_deletes_files(self):
        asset = AssetFactory.create()
        file_path = asset.file.path
        # Sanity precheck.
        with open(file_path, "r"):
            # File should exist-- this should be no problem.
            pass
        check_asset_associations(asset.id, force=True)
        with self.assertRaises(FileNotFoundError):
            with open(file_path, "r"):
                # Not anymore, though!
                pass

    def test_deletes_thumbnails(self):
        submission = SubmissionFactory.create()
        asset = submission.file
        thumbnail_paths = [thumbnail.path for thumbnail in asset.file.get_thumbnails()]
        self.assertTrue(thumbnail_paths)
        for path in thumbnail_paths:
            with open(path, "r"):
                # File should exist-- this should be no problem.
                pass
        submission.delete()
        check_asset_associations(asset.id, force=True)
        for path in thumbnail_paths:
            with self.assertRaises(FileNotFoundError):
                with open(path, "r"):
                    # Not anymore, though!
                    pass

    @patch("apps.lib.tasks.check_asset_associations")
    def test_auto_check(self, mock_check):
        submission = SubmissionFactory.create()
        asset_id = submission.file.id
        mock_check.apply_async.asset_called_with(asset_id, countdown=15)
