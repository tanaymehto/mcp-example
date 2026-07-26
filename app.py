from contextvars import ContextVar
import hashlib
import os
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
import uvicorn

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP("Exam MCP", transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))
_req: ContextVar[Request] = ContextVar("request")

@mcp.tool(
    name="solve_challenge",
    description="Solve the exam challenge."
)
async def solve_challenge(ctx: Context) -> str:
    req = _req.get()
    challenge = req.headers.get("X-Exam-Challenge", "")
    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode()
    ).hexdigest()[:16]

app = mcp.streamable_http_app()

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = _req.set(request)
        try:
            return await call_next(request)
        finally:
            _req.reset(token)

app.add_middleware(RequestContextMiddleware)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)