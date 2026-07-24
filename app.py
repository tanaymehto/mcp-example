import hashlib

from mcp.server.fastmcp import FastMCP, Context

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP("Exam MCP")


@mcp.tool(
    name="solve_challenge",
    description="Solve the exam challenge."
)
async def solve_challenge(ctx: Context) -> str:
    """
    Reads the challenge from HTTP headers and returns the
    first 16 hex chars of SHA256(challenge:email)
    """

    headers = ctx.request.headers

    challenge = headers.get("X-Exam-Challenge", "")

    digest = hashlib.sha256(
        f"{challenge}:{EMAIL}".encode()
    ).hexdigest()

    return digest[:16]


app = mcp.streamable_http_app()