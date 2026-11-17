---
name: alexa-plus-mcp-add-on-server
description: Build, review or debug a self-hosted MCP server meant to become an Alexa+ add-on (Streamable HTTP, stateless). Use when writing the /mcp endpoint, its initialize and protocol-version handling, its OAuth 2.1 account linking (401 behavior, discovery metadata, service vs user tokens), tool results that are spoken and shown as an MCP Apps card on an Echo Show, or when checking a server against the 500 ms latency budget. Includes a one-command wire check.
---

# Alexa+ MCP add-on server

This skill helps an agent build or review the **server side** of an Alexa+ add-on: a self-hosted MCP server over Streamable HTTP. It collects the requirements from the Alexa+ add-on pages and the MCP specification into one place, flags where the two disagree, and takes the tolerant path in each case so the server works with either reading.

**Scope and limits.** As of October 2026, the Alexa+ MCP Toolkit, CLI and web simulator are available to select partners only. Everything here comes from the published pages and was tested against self-built MCP clients, the official MCP Inspector and the official SDK client, **not** against the real Alexa+ client. Items the docs leave open are listed under "Plan around these" instead of being guessed. When the live Amazon docs say something different, the docs win.

## Check before applying rules

1. **Transport.** The server must answer `POST /mcp` over Streamable HTTP. A stdio-only server is out of scope.
2. **SDK.** Find the MCP SDK and its version. Rules that depend on SDK behavior name the TypeScript SDK 1.x (`WebStandardStreamableHTTPServerTransport` / `StreamableHTTPServerTransport`). For other SDKs, check the equivalent setting.
3. **Hosting.** Serverless (Lambda, Workers, Cloud Run) means no in-memory sessions, so the server must be stateless.

## Rules

### Transport and protocol

- **Accept `2025-03-26` and `2025-11-25` in `initialize`, and echo the client's version.** The "Create an MCP Add-on" page links the 2025-11-25 transport spec, but the example `initialize` on "Alexa+ MCP Client and App Lifecycle" sends `2025-03-26`.
- **Stateless JSON.** Issue no `Mcp-Session-Id` (TS SDK: `sessionIdGenerator: undefined`), answer with JSON (`enableJsonResponse: true`), create a fresh server per request, and return `405` for `GET /mcp`.
- **Do not 406 on `Accept`.** The TS SDK answers `406` unless `Accept` lists both `application/json` and `text/event-stream`. The Alexa+ client's request headers are not documented, so complete a missing or partial `Accept` before the request reaches the SDK. That is safe because the server only ever answers with JSON.
- **Origin.** Reject a foreign `Origin` with `403`. Allow requests with no `Origin` (server to server).
- **Keep `tools/list` byte-stable.** "Alexa+ refreshes tool information only on deployment." Snapshot-test `tools/list` across calls and both protocol versions, so a stray change can't slip in.
- **Bound every input.** Use `enum` for choices and `maxLength` on every string. Return tool failures as `isError` results, not as JSON-RPC protocol errors.

### Authorization

Full checklist: [references/auth-checklist.md](references/auth-checklist.md).

- **401 without `WWW-Authenticate`.** The Alexa+ authentication page lists `WWW-Authenticate` headers in 401 responses as unsupported, which differs from the MCP spec's default discovery. Keep the header behind a config flag if other clients need it.
- **Always serve discovery metadata at the well-known URIs:**
  - Protected Resource Metadata (RFC 9728) at `/.well-known/oauth-protected-resource`. `resource` must be the exact `/mcp` URI, and `authorization_servers` must list your issuer.
  - Authorization server metadata (RFC 8414) at `/.well-known/oauth-authorization-server`.
- **No Dynamic Client Registration.** The page lists it as unsupported.
- **Two kinds of token:**
  - `client_credentials` with scope `mcp:service`, and **no refresh token**. Use it to read the tool list.
  - User tokens through authorization code + **PKCE S256**, with `mcp:tools` / `mcp:resources`, `expires_in` of 3600 or less, and a refresh token that **rotates** on use.
- **A user-level tool called with a service token** gets `401` and `{"error":"unauthorized","message":"Access token required to use this tool."}`.
- **Client authentication:** accept HTTP Basic **and** credentials in the POST body. The pages disagree on which one is used.
- **Identity** is whatever your access token encodes. Put the account in `sub` and check that `aud` is your `/mcp` URI.

### Tool results: spoken and shown

- **Every tool returns three things:**
  - an `outputSchema`
  - `structuredContent`
  - a text content block that is a **complete spoken sentence** (an Echo Dot has no screen)
- **MCP Apps card:**
  - Serve one `ui://` resource as `text/html;profile=mcp-app`.
  - Reference it in **both** places: `_meta.ui.resourceUri` on the tool definition (MCP Apps, SEP-1865) **and** `_meta.ui` (`resourceUri`, `invoking`, `invoked`) on the tool result, where the Alexa+ lifecycle page shows it.
  - Keep the card self-contained under the default CSP: inline script and style, no external URLs. It talks to the host with `postMessage` (`ui/initialize`).
- **Say only what is safe to read aloud:** no URLs, no IDs, and times in the household's own time zone, never raw UTC.
- **Honest annotations:** set `readOnlyHint: true` only on tools that change nothing.

### Latency

- **Round trip under 500 ms** ("Create an MCP Add-on", Performance section). Keep models, third-party APIs and anything else slow off the tool path. Precompute, or do the work in a background job.
- **Cold starts break the budget first.** A Node Lambda with the full SDK measured 0.6–0.9 s cold and single-digit milliseconds warm. Lazy-load heavy modules and keep one instance warm on a schedule. Provisioned concurrency may be unavailable on a new account, whose concurrency quota can be 10.

### Policy

- **Crises:** the Policy Requirements (Sec. 13) ask add-ons to "redirect apparent references to personal crises or suicidal intent to emergency services or crisis hotlines". Implement the redirect in server code as a fixed reply, so no model wording can soften it.

## Plan around these (not documented as of October 2026)

- **Speaking first.** No documented way exists for an add-on to start a conversation: no reminders, notifications or routine invocation. Design so the person, or a household routine, starts the turn.
- **Utterance routing.** Whether a short phrase with no request in it ("good night") is ever offered to an add-on is not documented.
- **Request headers** the Alexa+ client sends are not documented. That's why the `Accept` rule above exists.
- **Real-client testing** is partner-only. Test with a self-built MCP client and MCP Inspector, and label any simulated Alexa+ client as simulated.

## Verify

Wire-level checks in one command, with zero dependencies. It runs both handshakes, statelessness, the JSON-only `Accept` case, `tools/list` stability, input bounds, `structuredContent`, Origin rejection, the 401 shape, both metadata documents, and a round trip against 500 ms:

```bash
npx github:Juiccef/mcp-handshake-check https://your-server.example/mcp --token "$TOKEN" --call <a-read-only-tool>
```

The official Inspector, as a second independent client:

```bash
npx @modelcontextprotocol/inspector@2.11.0 --cli https://your-server.example/mcp --transport http --header "Authorization: Bearer $TOKEN" --method tools/list
```

Both are helpers, not certification. Neither proves behavior inside Alexa+.

## Decision tree

```
Client gets 406                → Transport: complete the Accept header
Client can't find auth         → Authorization: PRM at the well-known URI; no WWW-Authenticate
Tool list read, tool call 401  → Authorization: service token vs user token
Card doesn't render            → Tool results: _meta.ui on definition AND result; no external URLs
Slow first answer              → Latency: cold start
Feature needs Alexa to start   → Plan around these: speaking first
```

## Sources

The Alexa+ add-on pages on developer.amazon.com: "Create an MCP Add-on", "Alexa+ MCP Client and App Lifecycle", "MCP authentication", "Account Linking for MCP Add-ons" and "Policy Requirements". Also the MCP specification 2025-11-25 (transport, authorization) and the MCP Apps extension (SEP-1865). Written while building [Closed Loop](https://github.com/Juiccef/closed-loop), whose test suite and `FRICTION_LOG.md` record each finding above. `mcp-handshake-check` is by the same author. Corrections are welcome.
