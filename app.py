import hashlib
from mcp.server.fastmcp import FastMCP, Context

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP("Exam MCP")

@mcp.tool(
    name="solve_challenge",
    description="Solve the exam challenge."
)
async def solve_challenge(ctx: Context) -> str:
    challenge = ctx.headers.get("X-Exam-Challenge", "")

    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode()
    ).hexdigest()[:16]


app = mcp.streamable_http_app()