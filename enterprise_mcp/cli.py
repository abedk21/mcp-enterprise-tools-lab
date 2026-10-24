"""Offline CLI for local demonstrations without the MCP SDK."""
import argparse
import json
from .service import Workspace


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--tenant',choices=['alpha','beta'],default='alpha')
    parser.add_argument('--role',choices=['viewer','analyst'],default='viewer')
    parser.add_argument('--query',default='oauth connector')
    args=parser.parse_args()
    ws=Workspace(args.tenant,args.role)
    print(json.dumps({'workspace':ws.describe(),'search':ws.search_knowledge(args.query),
                      'sample_ticket':ws.get_ticket('TKT-A-101' if args.tenant=='alpha' else 'TKT-B-201')},indent=2))


if __name__=='__main__':main()
