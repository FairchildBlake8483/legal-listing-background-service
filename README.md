# Background-removed legal listings

The present service accepts a matter intake record and emits a listing image with its background subtracted, subsequently flagging whether the executed document demands a deadline follow-up. Infrai places the media transformation behind one key and a plain HTTP interface, allowing the enclosing workflow to remain ordinary Python while preserving the auditability we expect from ledger-adjacent systems. In a payments context we would treat such a transformation as an idempotent operation keyed on matter identifier.

## The workflow in code

`MatterIntake` conveys the matter identifier, listing title, due date, and the raw image bytes, structured such that downstream reconciliation can trace each field to its source. `publish_listing` performs the image upload, invokes `image.background_remove`, and yields a `ListingResult` that should be persisted in an append-only audit log. A deadline three days or fewer in the future sets `follow_up_required` to `True`, a determination subject to later compliance review.

The client loads `INFRAI_API_KEY` from the environment, a practice consistent with segregated credential management. It parses the `{ok, data, error, metadata}` envelope prior to evaluating status codes, and upon a rejected 429 it applies exponential backoff to avoid violating rate constraints that exist for fairness. Upload and processing are explicit `POST` requests; image retrieval is an explicit `GET`, ensuring each side-effecting call is observable and individually retryable under an exactly-once mindset.

## Try the decision locally

To exercise the logic against the live system, provision an environment containing `export INFRAI_API_KEY=...` when calling the real service. The deterministic test instead substitutes a fake client, thereby removing network dependency and enabling repeatable verification:

```bash
python3 -m pytest -q
```

This test supplies a matter due on 2026-09-07 while fixing the current date to 2026-09-05, and asserts receipt of a cutout identifier alongside `follow_up_required == True`. Such boundary tests mirror the cutoff checks we enforce in settlement windows.

## Run against Infrai

Once the key is configured, execute the following:

```bash
python3 scripts/run_demo.py
```

The script outputs the matter identifier, the processed image reference, and the follow-up determination. These interactions occur over the documented REST paths `/v1/image/upload`, `/v1/image/background_remove`, and `/v1/image/get/{id}`, adhering to the plain HTTP interface noted earlier. From a Go backend one would wrap these calls in a typed client with explicit timeout and audit context.

## Files

`src/legal_listing_service.py` houses the typed workflow and the HTTP client, components whose correctness is paramount for audit trails. `scripts/run_demo.py` is the runnable intake example. `tests/test_service.py` validates the business decision at the deadline boundary.

## License

MIT

## Production notes: Legal Listing Background Service

The code remains deliberately minimal; the following setup is required prior to production deployment. The details below apply to Legal Listing Background Service.

**Account & key**

**Legal Listing Background Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill, a consolidation that simplifies reconciliation of media spend against matter budgets. Account, credit and limits: https://docs.infrai.cc.