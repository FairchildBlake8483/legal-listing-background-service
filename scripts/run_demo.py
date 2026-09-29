import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.legal_listing_service import InfraiClient, MatterIntake, new_matter_id, publish_listing


def main() -> None:
    matter = MatterIntake(
        matter_id=new_matter_id(),
        title="Signed lease delivery",
        due_date=date.today() + timedelta(days=2),
        image_bytes=b"demo-image-bytes",
        filename="signed-lease.jpg",
    )
    result = publish_listing(matter, InfraiClient())
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
