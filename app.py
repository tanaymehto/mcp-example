import hashlib
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount

from mcp.server.fastmcp import FastMCP

EMAIL = "23f2004044@ds.study.iitm.ac.in".strip().lower()

mcp = FastMCP(
    "Exam MCP",
    stateless_http=True,
    json_response=True,
)


@mcp.tool(name="solve_challenge")
async def solve_challenge(request: Request) -> str:
    """
    Returns first 16 hex chars of:
    SHA256(challenge:email)
    """

    challenge = request.headers.get("X-Exam-Challenge", "")

    digest = hashlib.sha256(
        f"{challenge}:{EMAIL}".encode()
    ).hexdigest()

    return digest[:16]


app = Starlette(
    routes=[
        Mount("/", app=mcp.streamable_http_app())
    ]
)