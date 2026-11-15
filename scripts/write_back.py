"""Use case 3, part two: write the ontology's answer back into Gravitino.

For each named column that is missing its expected tag, adds that tag to the
column through the Gravitino REST API, reads the tags back from Gravitino to
show they landed, then re-mirrors so Fuseki sees the change too.

Usage: ./write-back card                     one column, by column name
       ./write-back sales.orders.card        or by schema.table.column
       ./write-back --all                    every column missing its tag
"""

import subprocess
import sys

from lib import column_tags, tag_column
from sensitive import sensitive_columns

args = [a for a in sys.argv[1:]]
if not args:
    sys.exit(__doc__)

rows = [r for r in sensitive_columns() if r["missing"]]
if "--all" not in args:
    wanted = set(args)
    rows = [r for r in rows
            if r["columnName"] in wanted
            or r["column"] in wanted
            or r["column"].split(".", 1)[1] in wanted]

if not rows:
    print("Nothing to write: no matching sensitive column is missing its expected tag.")
    print("Run ./check-tags to see the current state.")
    sys.exit(0)

for r in rows:
    before = column_tags(r["table"], r["columnName"])
    tag_column(r["table"], r["columnName"], r["missingTags"])
    after = column_tags(r["table"], r["columnName"])
    print(f"{r['column']}")
    print(f"  ontology says: {r['category']}, so tag {', '.join(r['missingTags'])}")
    print(f"  Gravitino before: {', '.join(before) or 'no tags'}")
    print(f"  Gravitino after:  {', '.join(after)}   (read back from the Gravitino REST API)")

print()
subprocess.run([sys.executable, "mirror.py"], check=True)
