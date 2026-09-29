from datetime import date, timedelta

from src.legal_listing_service import MatterIntake, publish_listing


class FakeClient:
    def upload(self, content, filename):
        assert content == b"photo"
        assert filename.endswith(".jpg")
        return {"id": "uploaded-1"}

    def background_remove(self, image, fmt):
        assert image == "uploaded-1"
        assert fmt == "png"
        return {"id": "cutout-1"}


def test_due_soon_listing_requires_follow_up():
    matter = MatterIntake("m-1", "Intake packet", date(2026, 9, 7), b"photo", "packet.jpg")
    result = publish_listing(matter, FakeClient(), today=date(2026, 9, 5))
    assert result.background_removed_image == "cutout-1"
    assert result.follow_up_required is True


def test_distant_deadline_does_not_require_follow_up():
    matter = MatterIntake("m-2", "Court filing", date(2026, 9, 20), b"photo", "filing.jpg")
    assert publish_listing(matter, FakeClient(), today=date(2026, 9, 5)).follow_up_required is False
