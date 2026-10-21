# Device and platform realities (checked October 2026)

Always confirm against current official docs; these are the constraints that most often break demos.

## Ring Partner API (`https://api.amazonvision.com`)

- Server-to-server only: never call Ring OAuth/API from a browser or TV app (CORS, token exposure).
- Live view uses WHEP: `POST /v1/devices/{id}/media/streaming/whep/sessions` with
  `Content-Type: application/sdp`, a **recvonly** offer with ICE gathering complete; attach `ontrack`
  before setting the remote description; read the `201` SDP answer and `Location`; `DELETE` it after.
- Sessions are bounded: about **30 s for battery** and **60 s for line-powered** devices. A "watchdog"
  must therefore be a durable, event-driven record (webhooks + history + short sessions), and the UI
  should show `last observed` and coverage gaps.
- Developer Playground tokens last about **30 minutes**. Anything judged or used days later needs a
  conspicuously labelled recorded/simulated source — never a live-looking replay.
- Webhooks: verify `X-Signature: sha256=<HMAC_SHA256(raw_body)>`, dedupe by request id, and treat
  motion as a trigger to look, not as proof.

## Bee (`https://api.developer.bee.amazon.dev/v1/*`, Bearer token)

- SSE `GET /v1/stream?types=new-utterance,todo-created,...`; events carry an `event:` line.
- `new-utterance` data: `{"utterance": {"id", "text", "speaker", "spoken_at"|"start"}, "conversation_uuid"}`;
  `todo-created`: `{"todo": {"id", "text", "completed", "alarmAt"}}` (epoch ms) — per the official
  `bee-cli` stream formatter. Dedupe on the utterance/todo id, not the SSE id.
- Speaker labels do not say who the wearer is; unless configured, treat speech as unattributed and
  ask the owner to confirm the promise.
- Bee does not expose phone-call capture or haptic APIs publicly; don't design flows that need them.
- For Bee-track work, real device data is required — fixtures alone don't count.

## Fire TV

- Fire OS apps are Android apps (leanback launcher, banner, D-pad focus); Vega OS apps use React
  Native for Vega and run in the Vega Virtual Device on Linux/macOS. A browser tab is not a Fire TV app.
- Gate rewards inside your own app ("continue to entertainment"); there is no public API to lock or
  unlock other apps, and you must never imply one.
- Fire TV devices have no camera; a camera-based experience needs another source (e.g. a backend relay
  of an authorized camera) with honest source labels and an accessible non-camera alternative.

## Alexa+

- Integrations are MCP servers (Streamable HTTP, `2025-11-25`+) or Agent Skills. A web-based
  simulated Alexa experience must be labelled as simulated and must not claim device delivery
  (no "whispered to your earbuds" unless a real delivery API confirmed it).
