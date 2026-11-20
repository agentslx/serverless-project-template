"""Python sub-server for `language: "python"` routes.

The Rust local_proxy (port 9000) accepts every FE request and forwards
Python-language routes here over HTTP. We:
  1. Read the same `routes.json` the Rust proxy reads.
  2. For each entry with `language == "python"`, look up its handler module
     in `HANDLERS` and mount it on FastAPI.

To add a Python handler:
  1. Create the feature & handler under `feature/<x>_py/...`.
  2. Add the handler name to `HANDLERS` below.
  3. Add the route to `local_proxy/routes.json` with `language: "python"`.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, Response

# Make `backend/` importable so we can do `from feature.health_py...`
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from feature.health_py.presentation.lambda_handlers.health import handler as health_handler  # noqa: E402
from feature.auth_py.presentation.lambda_handlers.get_me import handler as get_me_handler  # noqa: E402
from feature.user_profile_py.presentation.lambda_handlers.get_profile import handler as get_profile_handler  # noqa: E402
from feature.user_profile_py.presentation.lambda_handlers.update_profile import handler as update_profile_handler  # noqa: E402
from feature.research_chat_py.presentation.lambda_handlers.get_conversation import handler as get_conversation_handler  # noqa: E402
from feature.research_chat_py.presentation.lambda_handlers.list_conversations import handler as list_conversations_handler  # noqa: E402

# handler-name → callable accepting the canonical proxy request dict.
HANDLERS = {
    "health":             health_handler.invoke,
    "get_me":             get_me_handler.invoke,
    "get_profile":        get_profile_handler.invoke,
    "update_profile":     update_profile_handler.invoke,
    "get_conversation":   get_conversation_handler.invoke,
    "list_conversations": list_conversations_handler.invoke,
}

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
log = logging.getLogger("local_proxy_py")

ROUTES_JSON = os.environ.get("ROUTES_JSON",
                             str(_BACKEND / "local_proxy" / "routes.json"))


def _load_routes() -> list[dict]:
    with open(ROUTES_JSON, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    return [r for r in cfg.get("routes", []) if r.get("language") == "python"]


def _to_pattern(path: str) -> str:
    """`/api/profile/:user_id` → `/api/profile/{user_id}` (FastAPI shape)."""
    return "/".join(
        "{" + s[1:] + "}" if s.startswith(":") else s
        for s in path.split("/")
    )


def _build_handler(handler_name: str):
    fn = HANDLERS.get(handler_name)
    if fn is None:
        raise RuntimeError(
            f"python handler '{handler_name}' is in routes.json but not registered "
            f"in local_proxy_py/main.py::HANDLERS"
        )

    async def _endpoint(request: Request):
        body_bytes = await request.body()
        try:
            body_json = json.loads(body_bytes) if body_bytes else None
        except json.JSONDecodeError:
            body_json = None
        proxy_req = {
            "method":      request.method,
            "path":        request.url.path,
            "headers":     {k.lower(): v for k, v in request.headers.items()},
            "path_params": dict(request.path_params),
            "json_body":   body_json,
        }
        out = fn(proxy_req)
        return Response(
            content=json.dumps(out["body"], default=str),
            status_code=out["status"],
            media_type="application/json",
        )

    return _endpoint


def _ws_chat_handler():
    """WebSocket endpoint for local chat agent streaming."""
    from fastapi import WebSocket, WebSocketDisconnect

    async def ws_chat(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("action", "")
                if action != "sendMessage":
                    await websocket.send_json({"type": "error", "error": f"Unknown action: {action}"})
                    continue

                content = data.get("content", "")
                conversation_id = data.get("conversation_id")
                generate_report = data.get("generate_report", False)

                if not content:
                    await websocket.send_json({"type": "error", "error": "Empty message"})
                    continue

                try:
                    from feature.research_chat_py.domain.agents.orchestrator import create_orchestrator
                    from feature.research_chat_py.data.datasources.s3_report_ds import S3ReportDataSource
                    from feature.research_chat_py.domain.entities.conversation import Message

                    orchestrator = create_orchestrator()
                    prompt = content
                    if generate_report:
                        prompt += "\n\n[Please generate a comprehensive markdown report for this query.]"

                    response = orchestrator(prompt)
                    full_text = str(response)

                    await websocket.send_json({"type": "chunk", "content": full_text})

                    msg = Message.new_assistant_message(content=full_text)
                    await websocket.send_json({
                        "type": "complete",
                        "message": msg.to_dict(),
                        "conversation_id": conversation_id,
                    })
                except Exception as e:
                    log.exception("Chat agent error")
                    await websocket.send_json({"type": "error", "error": str(e)})

        except WebSocketDisconnect:
            pass

    return ws_chat


def build_app() -> FastAPI:
    app = FastAPI(title="est local_proxy_py")

    @app.get("/__internal/healthz")
    def _healthz():
        return {"ok": True, "registered": list(HANDLERS.keys())}

    routes = _load_routes()
    log.info("mounting %d python routes", len(routes))
    for r in routes:
        method = r["method"].lower()
        pattern = _to_pattern(r["path"])
        endpoint = _build_handler(r["handler"])
        app.add_api_route(pattern, endpoint, methods=[method.upper()])
        log.info("  %s %s → %s", r["method"], pattern, r["handler"])

    # WebSocket endpoint for local chat streaming
    app.add_api_websocket_route("/ws/chat", _ws_chat_handler())
    log.info("  WS /ws/chat → research_chat agent")

    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "9001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
