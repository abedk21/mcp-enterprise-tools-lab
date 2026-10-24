"""SDK wiring test uses a fake MCPServer; protocol behavior not executed offline."""
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class MCPAdapterTests(unittest.TestCase):
    def test_v2_sdk_tool_resource_contract(self):
        registrations={'tools':[],'resources':[]}
        class FakeMCPServer:
            def __init__(self,name):self.name=name
            def tool(self):
                def register(fn):registrations['tools'].append(fn);return fn
                return register
            def resource(self,uri):
                def register(fn):registrations['resources'].append((uri,fn));return fn
                return register
        mcp=types.ModuleType('mcp');mcp.__path__=[]
        mcp_server=types.ModuleType('mcp.server');mcp_server.MCPServer=FakeMCPServer
        path=Path(__file__).parents[1]/'server.py'
        spec=importlib.util.spec_from_file_location('demo_mcp_server',path)
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'mcp':mcp,'mcp.server':mcp_server}),patch.dict('os.environ',{'MCP_DEMO_TENANT':'alpha','MCP_DEMO_ROLE':'viewer'}):
            spec.loader.exec_module(module)
        self.assertEqual(module.mcp.name,'synthetic-enterprise-support-tools')
        self.assertEqual({fn.__name__ for fn in registrations['tools']},
                         {'search_knowledge','get_ticket','get_runbook','draft_handoff'})
        self.assertEqual(registrations['resources'][0][0],'workspace://metadata')
        self.assertEqual(module.get_ticket('TKT-B-201'),{'error':'not_found'})
        self.assertEqual(json.loads(module.workspace_metadata())['tenant'],'alpha')


if __name__=='__main__': unittest.main()
