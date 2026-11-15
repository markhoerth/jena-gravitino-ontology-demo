"""Use case 3, part one: which sensitive columns are missing the tag the ontology expects?

The ontology names a canonical tag for each data category (acme:canonicalTag):
pii for Personal data, pci for Payment card, financial for Account balance.
A column found sensitive should carry the canonical tag of its category.
Reads Fuseki only; run ./mirror first if tags changed in Gravitino.
"""

from lib import print_table
from sensitive import sensitive_columns

rows = sensitive_columns()
missing = [r for r in rows if r["missing"]]

print("Sensitive columns and the tag the ontology expects:\n")
print_table(["column", "category", "expected", "hasTags"], rows)

if missing:
    print(f"\n{len(missing)} column(s) are missing their expected tag:")
    for r in missing:
        have = r["hasTags"] or "no tags"
        print(f"  {r['column']}: expects {', '.join(r['missingTags'])}, has {have}")
    print("\nFix one:  ./write-back card      Fix all:  ./write-back --all")
else:
    print("\nEvery sensitive column carries its expected tag.")
