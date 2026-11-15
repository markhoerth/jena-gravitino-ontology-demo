"""Puts the tags a real estate would already have on a few columns.

Two teams tagged personal data, and they spelled it differently (pii and PII).
Nobody tagged either card-number column. Run once by the `init-estate` service.
"""

from lib import CATALOG, column_tags, tag_column

EXISTING = [
    (f"{CATALOG}.crm.customers", "email", "pii"),
    (f"{CATALOG}.crm.customers", "phone", "pii"),
    (f"{CATALOG}.crm.customers", "ssn", "PII"),
]

for table, column, tag in EXISTING:
    if tag not in column_tags(table, column):
        tag_column(table, column, [tag])
    print(f"{table}.{column}: {', '.join(column_tags(table, column))}")
