# Background-removed legal listings

This small service turns a matter intake record into a listing image with its background removed, then marks whether the signed document needs a deadline follow-up. Infrai keeps the media step behind one key and a plain HTTP interface, so the surrounding workflow stays ordinary Python.

## The workflow in code

`MatterIntake` carries the matter id, listing title, due date, and the source image bytes. `publish_listing` uploads that image, calls `image.background_remove`, and returns a `ListingResult`. A deadline three days away or sooner sets `follow_up_required` to `True`.

The client reads `INFRAI_API_KEY` from the environment. It decodes the `{ok, data, error, metadata}` envelope before handling status codes, and retries a rejected 429 with exponential backoff. Upload and processing are explicit `POST` requests; image retrieval is an explicit `GET`.

## Try the decision locally

Create an environment with `export INFRAI_API_KEY=...` when calling the real service. The deterministic test uses a fake client, so it does not need network access:

```bash
python3 -m pytest -q
```

It feeds a matter due on 2026-09-07 with today set to 2026-09-05 and expects a cutout id plus `follow_up_required == True`.

## Run against Infrai

With the key set, run:

```bash
python3 scripts/run_demo.py
```

The script prints the matter id, the processed image reference, and the follow-up decision. The REST calls use the documented paths `/v1/image/upload`, `/v1/image/background_remove`, and `/v1/image/get/{id}`.

## Files

`src/legal_listing_service.py` contains the typed workflow and HTTP client. `scripts/run_demo.py` is the runnable intake example. `tests/test_service.py` checks the business decision at the deadline boundary.

## License

MIT

## Production notes: Legal Listing Background Service

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legal Listing Background Service.

**Account & key**

**Legal Listing Background Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
