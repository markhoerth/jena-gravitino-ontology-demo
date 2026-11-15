"""Use case 2: ask the ontology which columns hold sensitive data.

Reads Fuseki only. Gravitino is not called: the answer comes from the ontology,
the links and the mirrored copy of the estate sitting together in one store.
If you changed tags in Gravitino since the last mirror, run ./mirror first.
"""

from lib import print_table
from sensitive import QUERY, sensitive_columns

rows = sensitive_columns()
print("Columns the ontology says hold sensitive data:\n")
print_table(["column", "category", "foundBy", "hasTags"], rows)

untagged = [r["column"] for r in rows if not r["hasTags"]]
if untagged:
    print("\nNobody ever tagged these, and they were still found:")
    for col in untagged:
        print(f"  {col}")
print("\nNot found: lakehouse.games.sessions.card_game_id. It has 'card' in its name,"
      "\nbut its concept (Game identifier) is Operational data, not Sensitive data.")
print("\nSPARQL used (also in scripts/sensitive.py):" + QUERY)
