from contextvars import ContextVar
import hashlib
import os
from starlette.requests import Request
from mcp.server.fastmcp import FastMCP, Context
import uvicorn

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP("Exam MCP")
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

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    token = _req.set(request)
    try:
        return await call_next(request)
    finally:
        _req.reset(token)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)