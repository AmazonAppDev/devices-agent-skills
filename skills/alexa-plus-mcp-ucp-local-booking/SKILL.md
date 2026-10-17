
---
name: alexa-plus-mcp-ucp-local-booking
description: Complete architecture guide and pattern reference for building Alexa+ Add-Ons using Model Context Protocol (MCP 2025-11-25 Streamable HTTP), Interactive MCP Apps (ui:// resources with text/html;profile=mcp-app), Universal Commerce Protocol (UCP 2026-01-11), and Alexa+ Local Booking SPI.
license: MIT
compatibility: '>=1.0.0'
metadata:
  author: FirstFix MCP Team (Amazon Developer Hackathon 2026)
  version: 1.0.0
  homepage: https://github.com/firstfix-mcp/firstfix-mcp-alexa-plus
  category: alexa-plus-integrations
---

# Alexa+ MCP, UCP & Local Booking Architecture Guide

This skill equips AI developer agents (Claude Code, Cursor, Google Antigravity, Kiro) with end-to-end patterns to design, implement, and deploy production-grade **Alexa+ Add-Ons**.

---

## 1. Core Architecture Principles

1. **Protocol Standards**:
   - **MCP Specification**: Use `2025-11-25` over Streamable HTTP (`POST /mcp`).
   - **Interactive UI**: Serve HTML resources using `mimeType: "text/html;profile=mcp-app"` over custom `ui://` schemes.
   - **Commerce**: Implement Universal Commerce Protocol (UCP) version `2026-01-11` (`dev.ucp.shopping.checkout`) with strict 24-hour `Idempotency-Key` deduplication.
   - **Local Booking SPI**: Maintain immutable `correlationToken` bridging across checkout, appointment dispatch, and physical arrival.

2. **The 4 Common Integration Pitfalls & How to Avoid Them**:
   - **Pitfall 1 (MCP Accept Header Mismatch)**: Some MCP proxies send `Accept: application/json`, whereas MCP streamable servers expect `text/event-stream`. Solution: Always accept and negotiate both `application/json, text/event-stream`.
   - **Pitfall 2 (Idempotency Mutation 409 Conflict)**: When an `Idempotency-Key` is replayed with a altered request payload, RFC guidelines mandate returning `409 Conflict`, NOT the cached response!
   - **Pitfall 3 (Add-On Asset Dimensions)**: Amazon's package validator rejects non-conforming PNGs in `addon.json`. Icons must be strictly `512x512` and hero carousels `1200x800`.
   - **Pitfall 4 (MCP App postMessage Bridge)**: Sandboxed MCP App iframes must use JSON-RPC 2.0 messages with `ui/initialize`, `tools/call`, and `ui/message` carrying `action: "initiate_checkout"`.

---

## 2. Interactive MCP App JSON-RPC 2.0 Bridge

In any `ui://` resource with `text/html;profile=mcp-app`, include the bidirectional `postMessage` protocol:

```javascript
// 1. Handshake with Echo Show 15 host
window.parent.postMessage({
  jsonrpc: '2.0',
  method: 'ui/initialize',
  params: {
    appUri: 'ui://firstfix/stocked-pro-carousel.html',
    viewport: { width: window.innerWidth, height: window.innerHeight },
    theme: 'dark'
  }
}, '*');

// 2. Trigger 1-Tap UCP Checkout in Alexa+ Host
function triggerCheckout(checkoutData) {
  window.parent.postMessage({
    jsonrpc: '2.0',
    method: 'ui/message',
    params: {
      role: 'user',
      content: [{ type: 'text', text: JSON.stringify(checkoutData) }]
    }
  }, '*');
}
```

---

## 3. UCP Checkout State Machine

Implement the strict UCP lifecycle:
1. `POST /checkout-sessions` -> Creates session (`status: "incomplete"`).
2. `PUT /checkout-sessions/:id` -> Updates slot / billing items (`status: "ready_for_complete"`).
3. `POST /checkout-sessions/:id/complete` -> Collects payment confirmation and locks inventory (`status: "completed"`).
4. `POST /checkout-sessions/:id/cancel` -> Releases held inventory and resets session (`status: "cancelled"`).

---

## 4. Cryptographic Correlation Linking

Link all 3 subsystems using a shared token:
```
[UCP Checkout Session] ===(correlationToken)===> [Local Booking SPI] ===(correlationToken)===> [Ring Smart Access]
```
This guarantees that technician arrival verification at a Ring doorbell camera matches the exact OEM part and homeowner dispatch order.
