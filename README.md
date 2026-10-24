# MCP Enterprise Tools Lab

A **read-only enterprise support tool server using the current MCP Python SDK v2 (`MCPServer`)**. Serves tools and a resource over stdio, backed by synthetic, tenant-labeled knowledge, tickets, and runbooks. All sensitive operations are absent: no live SaaS integrations, credentials, authentication, network listeners, or writes.

## What it demonstrates

- **Four MCP tools**: `search_knowledge`, `get_ticket`, `get_runbook`, and `draft_handoff`.
- **One MCP resource**: `workspace://metadata`.
- **Process-scoped tenant and viewer/analyst fixtures**: filtering happens in code before data reaches tool responses; tenant and role are never selectable by a model-supplied tool parameter.
- **Missing/unauthorized indistinguishability** for ticket lookups to avoid leaking synthetic existence.
- **Least-privilege visibility**, bounded retrieval, safe handoff evidence references, and explicit marking of untrusted document text.
- **Mocked MCP registration tests** plus deterministic offline tenant-isolation tests.

## Architecture

```text
MCP client or Inspector
       | stdio transport only (local host starts server subprocess)
       v
 Official MCP v2 MCPServer  <-- tool / resource registry
       | trusted process configuration (MCP_DEMO_TENANT, MCP_DEMO_ROLE)
       v
 enterprise_mcp.service.Workspace
       |-- tenant-scope / visibility checks
       |-- synthetic docs and ticket retrieval
       +-- draft-only handoff packets
```

## Run offline (Python 3.11+, no dependencies)

```bash
python -m enterprise_mcp.cli --tenant alpha --role viewer --query oauth
python -m enterprise_mcp.cli --tenant beta --role analyst --query quota
python -m unittest discover -s tests -v
```

## Run the real MCP v2 server (optional)

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
pip install -e '.[mcp]'
MCP_DEMO_TENANT=alpha MCP_DEMO_ROLE=viewer python server.py
```

`server.py` starts **stdio** transport and waits for a host; it is **not an interactive CLI** and intentionally prints nothing. Configure your MCP host to launch the server subprocess. Optionally use `mcp dev server.py` with MCP Inspector, as described in [official SDK docs](https://py.sdk.modelcontextprotocol.io/). For a different synthetic workspace, change the launching process's environment variables; they are fixed for that server process.

## Important security boundary

**This is not a production authenticated, multi-tenant MCP service.** Environment variables are trusted *demo configuration*, not an identity mechanism. Any caller attached to the same server process sees the same workspace. Do not expose this server over HTTP, share the process with untrusted clients, pass real tokens or customer data, or interpret role selection as authentication. Real deployment requires host-verified identity, authorization on each call, threat modeling, structured audit trails, and appropriate secret handling.

Retrieved text (including a malicious-looking synthetic document) is labeled untrusted; labeling alone is not proof of prompt-injection resistance. The server never creates tickets or writes to external systems.

## Reference

MCP Python SDK v2: https://py.sdk.modelcontextprotocol.io/
