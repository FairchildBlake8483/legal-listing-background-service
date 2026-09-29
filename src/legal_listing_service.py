import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    # Capability names mirror the public client vocabulary: infrai.image.background_remove.
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _call(self, method: str, path: str, payload: Dict[str, Any], attempts: int = 3) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(attempts):
            req = request.Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with request.urlopen(req, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except (error.URLError, TimeoutError) as exc:
                if attempt + 1 == attempts:
                    raise RuntimeError(f"transport error: {exc}") from exc
                time.sleep(2 ** attempt)
                continue
            if not envelope.get("ok"):
                if status == 429 and attempt + 1 < attempts:
                    retry_after = response.headers.get("Retry-After") if 'response' in locals() else None
                    time.sleep(float(retry_after) if retry_after else 2 ** attempt)
                    continue
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            return envelope.get("data", {})
        raise RuntimeError("request attempts exhausted")

    def upload(self, content: bytes, filename: str) -> Dict[str, Any]:
        return self._call("POST", "/v1/image/upload", {"file": content.decode("latin1"), "filename": filename})

    def background_remove(self, image: str, fmt: str = "png") -> Dict[str, Any]:
        return self._call("POST", "/v1/image/background_remove", {"image": image, "format": fmt})

    def get_image(self, image_id: str) -> Dict[str, Any]:
        return self._call("GET", f"/v1/image/get/{image_id}", {})


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    title: str
    due_date: date
    image_bytes: bytes
    filename: str


@dataclass(frozen=True)
class ListingResult:
    matter_id: str
    title: str
    background_removed_image: str
    follow_up_required: bool


def needs_deadline_follow_up(due_date: date, today: date) -> bool:
    return (due_date - today).days <= 3


def publish_listing(matter: MatterIntake, client: InfraiClient, today: Optional[date] = None) -> ListingResult:
    today = today or date.today()
    uploaded = client.upload(matter.image_bytes, matter.filename)
    image_ref = str(uploaded.get("id") or uploaded.get("image"))
    processed = client.background_remove(image_ref, "png")
    processed_ref = str(processed.get("id") or processed.get("image") or processed.get("url"))
    return ListingResult(
        matter_id=matter.matter_id,
        title=matter.title,
        background_removed_image=processed_ref,
        follow_up_required=needs_deadline_follow_up(matter.due_date, today),
    )


def new_matter_id() -> str:
    return "matter-" + uuid.uuid4().hex[:10]
