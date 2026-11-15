"""One-time setup, run by the `init` service on `docker compose up`.

1. Creates the `acme` metalake and the `lakehouse` Iceberg catalog in Gravitino.
2. Creates the tags the demo uses.
3. Loads the ontology and the links into Fuseki.

Spark creates the tables afterwards (seed/seed.sql), then `estate_tags.py` and
`mirror.py` run. Safe to run more than once.
"""

from lib import (CATALOG, FUSEKI, GRAPH_LINKS, GRAPH_ONTOLOGY, GRAVITINO, METALAKE,
                 ensure_tag, gravitino, put_graph, wait_for)

wait_for(GRAVITINO + "/api/version", "Gravitino")
wait_for(FUSEKI + "/sparql?query=ASK%7B%7D", "Fuseki")

status, _ = gravitino("POST", "/metalakes",
                      {"name": METALAKE, "comment": "Acme demo metalake", "properties": {}},
                      ok=(200, 409))
print(f"metalake {METALAKE}: {'created' if status == 200 else 'already there'}")

status, _ = gravitino("POST", f"/metalakes/{METALAKE}/catalogs", {
    "name": CATALOG,
    "type": "RELATIONAL",
    "provider": "lakehouse-iceberg",
    "comment": "Iceberg tables, served to Spark through the Iceberg REST service",
    "properties": {
        "catalog-backend": "jdbc",
        "uri": "jdbc:postgresql://postgres:5432/iceberg",
        "jdbc-driver": "org.postgresql.Driver",
        "jdbc-user": "iceberg",
        "jdbc-password": "iceberg",
        "jdbc-initialize": "true",
        "warehouse": "file:///data/warehouse",
    },
}, ok=(200, 409))
print(f"catalog {CATALOG}: {'created' if status == 200 else 'already there'}")

for name, comment in [
    ("pii", "Personal data"),
    ("PII", "Personal data (another team's spelling)"),
    ("pci", "Payment card data"),
    ("financial", "Account balances"),
]:
    created = ensure_tag(name, comment)
    print(f"tag {name}: {'created' if created else 'already there'}")

for graph, path in [(GRAPH_ONTOLOGY, "/ontology/acme.ttl"), (GRAPH_LINKS, "/ontology/links.ttl")]:
    with open(path, encoding="utf-8") as f:
        put_graph(graph, f.read())
    print(f"loaded {path} into Fuseki graph {graph}")
