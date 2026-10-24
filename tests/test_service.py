import copy
import json
import os
from unittest.mock import patch
import unittest
from enterprise_mcp.service import Workspace, FIXTURES


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.a=Workspace('alpha','viewer');self.b=Workspace('beta','viewer');self.analyst=Workspace('alpha','analyst')

    def test_bad_tenant(self):
        with self.assertRaises(ValueError):Workspace('gamma','viewer')
    def test_bad_role(self):
        with self.assertRaises(ValueError):Workspace('alpha','superadmin')
    def test_default_env(self):
        with patch.dict(os.environ,{},clear=True):self.assertEqual(Workspace.from_env().describe()['role'],'viewer')
    def test_process_profile(self):
        with patch.dict(os.environ,{'MCP_DEMO_TENANT':'beta','MCP_DEMO_ROLE':'analyst'}):
            w=Workspace.from_env();self.assertEqual((w.tenant,w.role),('beta','analyst'))
    def test_cross_tenant_search_separation(self):
        self.assertFalse(self.a.search_knowledge('quota')['matches'])
        self.assertEqual(self.b.search_knowledge('quota')['matches'][0]['id'],'DOC-B-1')
    def test_viewer_cannot_read_restricted_article(self):
        self.assertFalse(self.a.search_knowledge('escalation tips')['matches'])
    def test_analyst_can_read_restricted_article(self):
        self.assertIn('DOC-A-2',[x['id'] for x in self.analyst.search_knowledge('escalation tips')['matches']])
    def test_restricted_article_not_in_beta(self):
        self.assertFalse(self.b.search_knowledge('Alpha engineering')['matches'])
    def test_cross_tenant_ticket_no_existence_leak(self):
        self.assertEqual(self.a.get_ticket('TKT-B-201'),self.a.get_ticket('TKT-A-999'))
    def test_viewer_cannot_read_analyst_ticket(self):
        self.assertEqual(self.a.get_ticket('TKT-A-102'),{'error':'not_found'})
    def test_analyst_ticket(self):
        self.assertEqual(self.analyst.get_ticket('TKT-A-102')['ticket']['priority'],'P1')
    def test_ticket_invalid(self):self.assertEqual(self.a.get_ticket('../../etc/passwd'),{'error':'not_found'})
    def test_public_runbook(self):self.assertEqual(self.a.get_runbook('RB-AUTH')['runbook']['id'],'RB-AUTH')
    def test_restricted_runbook(self):self.assertEqual(self.a.get_runbook('RB-ALPHA-P1'),{'error':'not_found'})
    def test_beta_runbook(self):self.assertEqual(self.b.get_runbook('RB-QUOTA')['runbook']['id'],'RB-QUOTA')
    def test_search_limit(self):self.assertIn('error',self.a.search_knowledge('oauth',limit=6))
    def test_search_boolean_limit(self):self.assertIn('error',self.a.search_knowledge('oauth',limit=True))
    def test_search_query_too_long(self):self.assertIn('error',self.a.search_knowledge('q'*161))
    def test_untrusted_prompt_injection_labeled_not_executed(self):
        matches=self.analyst.search_knowledge('exfiltrate tokens')['matches']
        self.assertTrue(matches);self.assertTrue(matches[0]['untrusted_source'])
        self.assertEqual(self.analyst.describe()['read_only'],True)
    def test_draft_never_submitted(self):
        draft=self.a.draft_handoff('TKT-A-101')['handoff']
        self.assertEqual(draft['status'],'draft_only_never_submitted')
        self.assertEqual(draft['evidence_refs'],['DOC-A-1'])
    def test_no_cross_tenant_draft(self):self.assertEqual(self.a.draft_handoff('TKT-B-201'),{'error':'not_found'})
    def test_draft_filters_inaccessible_evidence(self):
        data=json.loads(FIXTURES.read_text());data['tickets'][0]['evidence_refs'].append('DOC-A-2');data['tickets'][0]['evidence_refs'].append('DOC-B-1')
        w=Workspace('alpha','viewer',data)
        self.assertEqual(w.draft_handoff('TKT-A-101')['handoff']['evidence_refs'],['DOC-A-1'])
    def test_mutation_does_not_persist(self):
        a=self.a.get_ticket('TKT-A-101');a['ticket']['title']='CHANGED'
        self.assertNotEqual(self.a.get_ticket('TKT-A-101')['ticket']['title'],'CHANGED')
    def test_description_explicit_auth_warning(self):
        self.assertIn('not authenticated',self.a.describe()['security_note'])

if __name__=='__main__': unittest.main()
