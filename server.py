"""Official MCP Python SDK v2 server, stdio-only for local demonstration.

Install `pip install -e '.[mcp]'`. Do NOT expose via HTTP; this sample has no
identity verification, OAuth validation, or authenticating gateway.
"""
import json
from mcp.server import MCPServer
from enterprise_mcp.service import Workspace

# Scope is fixed when the host starts this process, not supplied by the LLM.
workspace = Workspace.from_env()
mcp = MCPServer('synthetic-enterprise-support-tools')


@mcp.tool()
def search_knowledge(query: str, limit: int = 3) -> dict:
    """Search visible synthetic runbook articles; all returned content is untrusted."""
    return workspace.search_knowledge(query, limit)


@mcp.tool()
def get_ticket(ticket_id: str) -> dict:
    """Read a synthetic ticket in the preselected tenant and role."""
    return workspace.get_ticket(ticket_id)


@mcp.tool()
def get_runbook(runbook_id: str) -> dict:
    """Read a tenant-scoped synthetic engineering runbook."""
    return workspace.get_runbook(runbook_id)


@mcp.tool()
def draft_handoff(ticket_id: str) -> dict:
    """Prepare a synthetic escalation draft without submitting or changing anything."""
    return workspace.draft_handoff(ticket_id)


@mcp.resource('workspace://metadata')
def workspace_metadata() -> str:
    """Describe which synthetic workspace this MCP process exposes."""
    return json.dumps(workspace.describe())


if __name__ == '__main__':
    # Default is stdio: no listening network socket or port.
    mcp.run()
