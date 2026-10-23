from __future__ import annotations
from typing import Any, Dict


class McpResponseInjector:
    """Wraps the ASGI send callable to inject MCP 2025-11-25 CORS headers (Max 2 methods)."""

    def __init__(self, send_callable: Any, origin_bytes: bytes) -> None:
        if not callable(send_callable):
            raise ValueError("Invariant violation: send_callable must be an asynchronous callable.")
        self._send = send_callable
        self._origin = origin_bytes

    async def __call__(self, message: Dict[str, Any]) -> None:
        """Intercepts http.response.start to append required session exposure headers."""
        if message.get("type") == "http.response.start":
            headers = list(message.get("headers", []))
            headers.append((b"access-control-expose-headers", b"Mcp-Session-Id"))
            headers.append((b"access-control-allow-headers", b"Content-Type, Mcp-Session-Id"))
            headers.append((b"access-control-allow-origin", self._origin))
            message["headers"] = headers
        await self._send(message)


class McpCorsMiddleware:
    """Intercepts ASGI lifecycles to guarantee Streamable HTTP session continuity (Max 2 methods)."""

    def __init__(self, app: Any, allowed_origin: str = "*") -> None:
        if not callable(app):
            raise ValueError("Invariant violation: app must be a valid ASGI application.")
        self._app = app
        self._origin = allowed_origin.encode("utf-8")

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Evaluates protocol scope and routes to either a fast-path OPTIONS return or the injector."""
        if scope.get("type") != "http":
            return await self._app(scope, receive, send)

        if scope.get("method") == "OPTIONS":
            await send({
                "type": "http.response.start",
                "status": 204,
                "headers": [
                    (b"access-control-expose-headers", b"Mcp-Session-Id"),
                    (b"access-control-allow-headers", b"Content-Type, Mcp-Session-Id"),
                    (b"access-control-allow-origin", self._origin),
                ],
            })
            return await send({"type": "http.response.body", "body": b""})

        injector = McpResponseInjector(send_callable=send, origin_bytes=self._origin)
        return await self._app(scope, receive, injector)
      
