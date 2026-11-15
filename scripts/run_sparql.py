"""Run any SPARQL SELECT against Fuseki and print the result as a table.

Usage: ./sparql queries/04-customer-data.rq
       ./sparql 'PREFIX acme: <http://example.org/acme#> SELECT * WHERE { ?c acme:canonicalTag ?t }'
"""

import os
import sys

from lib import print_table, sparql

if len(sys.argv) < 2:
    sys.exit(__doc__)

arg = sys.argv[1]
path = arg if os.path.isabs(arg) else os.path.join("/", arg)
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        query = f.read()
else:
    query = arg

columns, rows = sparql(query)
print_table(columns, rows)
