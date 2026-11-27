"""Local synthetic read-only MCP server; no corporate system is contacted."""

from mcp.server import MCPServer

server = MCPServer("phase0-fixture")


@server.tool()
def read_fixture() -> str:
    """Return a fixed synthetic evidence identifier."""
    return "fixture-evidence"


if __name__ == "__main__":
    server.run(transport="stdio")
