# OAuth 2.1 checklist for an Alexa+ MCP add-on

Collected from three Alexa+ pages ("MCP Toolkit Authentication", "MCP authentication" and "Account Linking for MCP Add-ons"), which split the requirements between them and disagree in places. Where they disagree, accept both forms.

## Discovery

- [ ] `401` for a missing or invalid token, **without** a `WWW-Authenticate` header.
- [ ] `GET /.well-known/oauth-protected-resource` returns:
  - `resource`: the exact `/mcp` URI, derived from the request so it matches the public host
  - `authorization_servers`: your issuer
- [ ] `GET /.well-known/oauth-authorization-server` returns:
  - `issuer`
  - `authorization_endpoint`, `token_endpoint` and `revocation_endpoint`
  - `code_challenge_methods_supported: ["S256"]`
  - `grant_types_supported` with `authorization_code`, `refresh_token` and `client_credentials`
  - `response_types_supported: ["code"]`
  - `scopes_supported` with `mcp:tools`, `mcp:resources` and `mcp:service`
- [ ] No `registration_endpoint`. Dynamic Client Registration is listed as unsupported.

## Service token (Alexa+ reading your tools)

- [ ] `grant_type=client_credentials`, `scope=mcp:service`.
- [ ] **No refresh token** in the response.
- [ ] `tools/list` works with it.
- [ ] A user-level `tools/call` with it gets `401` and `{"error":"unauthorized","message":"Access token required to use this tool."}`.

## User tokens (account linking)

- [ ] Authorization code with **PKCE S256 only**: refuse `plain` and a missing challenge.
- [ ] `resource` on the authorize and token requests must equal the `/mcp` URI. The account linking page says `resource` **is not sent on refresh**, so don't require it there.
- [ ] Redirect only to registered redirect URIs. Never redirect to an unregistered one, even to report an error.
- [ ] Return `state` (and `iss`) on the redirect. A cancel returns `error=access_denied` with the `state`.
- [ ] A code works **once**, and only with its verifier.
- [ ] Access token: `expires_in` of 3600 or less, `Cache-Control: no-store`.
- [ ] A refresh token comes with every user access token and **rotates** on use: the new one works, the old one stops.
- [ ] Revocation (RFC 7009) stops a refresh token from working.

## Client authentication

- [ ] Accept HTTP Basic (`client_id:client_secret`).
- [ ] Also accept `client_id` and `client_secret` in the POST body. The checklist allows either, and one example shows the body form.

## On `/mcp`

- [ ] Reject a tampered, expired, wrong-audience (`aud` is not your `/mcp` URI) or wrong-scope token with `401`.
- [ ] Bearer tokens in the query string are refused; send them only in the `Authorization` header.
- [ ] The account a tool acts for comes from the token (`sub`), never from tool arguments.
