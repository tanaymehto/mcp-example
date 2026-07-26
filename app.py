import hashlib
import json
import os
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
import uvicorn

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP("Exam MCP", transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))

LATEST_CHALLENGE = ""
CHALLENGES_BY_ID = {}

@mcp.tool(
    name="solve_challenge",
    description="Solve the exam challenge."
)
async def solve_challenge(ctx: Context) -> str:
    global LATEST_CHALLENGE
    msg_id = None
    if hasattr(ctx, "request_id"): msg_id = ctx.request_id
    elif hasattr(ctx, "request_context"):
        rc = ctx.request_context
        if hasattr(rc, "request_id"): msg_id = rc.request_id
        elif hasattr(rc, "meta") and hasattr(rc.meta, "id"): msg_id = rc.meta.id
        elif hasattr(rc, "message_id"): msg_id = rc.message_id
    
    challenge = CHALLENGES_BY_ID.get(msg_id) if (msg_id and msg_id in CHALLENGES_BY_ID) else LATEST_CHALLENGE
    if not challenge:
        challenge = LATEST_CHALLENGE
        
    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode()
    ).hexdigest()[:16]

app = mcp.streamable_http_app()

class ChallengeMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        global LATEST_CHALLENGE
        if scope["type"] == "http":
            challenge = next((v.decode("latin1") for k, v in scope["headers"] if k.lower() == b"x-exam-challenge"), "")
            if challenge:
                LATEST_CHALLENGE = challenge
                body = b""
                more_body = True
                messages = []
                while more_body:
                    message = await receive()
                    messages.append(message)
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        msg_id = data.get("id")
                        if msg_id is not None:
                            CHALLENGES_BY_ID[msg_id] = challenge
                except Exception:
                    pass
                
                async def new_receive():
                    if messages:
                        return messages.pop(0)
                    return {"type": "http.disconnect"}
                
                return await self.app(scope, new_receive, send)
        
        return await self.app(scope, receive, send)

app.add_middleware(ChallengeMiddleware)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)