"""The one SPARQL query the find, check and write-back steps all share.

For every column the ontology says is sensitive, it returns:
  column     the Gravitino column, e.g. lakehouse.sales.orders.card
  category   the data categories it holds, e.g. PaymentCard
  foundBy    "link" (links.ttl names it), "tag" (it carries a tag that stands for
             a sensitive category), or both
  expected   the canonical tag(s) for those categories, from acme.ttl
  hasTags    the tags Gravitino had on the column at the last mirror
"""

from lib import require_estate, sparql

QUERY = """
PREFIX acme: <http://example.org/acme#>
PREFIX gv:   <http://example.org/gravitino#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?column ?table ?columnName
       (GROUP_CONCAT(DISTINCT STRAFTER(STR(?category), "#"); separator=", ") AS ?category)
       (GROUP_CONCAT(DISTINCT ?road; separator=", ")    AS ?foundBy)
       (GROUP_CONCAT(DISTINCT ?canon; separator=", ")   AS ?expected)
       (GROUP_CONCAT(DISTINCT ?tagName; separator=", ") AS ?hasTags)
WHERE {
  {
    ?concept acme:hasDataCategory ?category ; acme:storedIn ?col .
    BIND("link" AS ?road)
  } UNION {
    ?col gv:hasTag ?t . ?t acme:standsFor ?category .
    BIND("tag" AS ?road)
  }
  ?category rdfs:subClassOf* acme:SensitiveData .
  ?col gv:fullName ?column ; gv:name ?columnName ; gv:inTable / gv:fullName ?table .
  OPTIONAL { ?category rdfs:subClassOf* ?anc . ?anc acme:canonicalTag ?canon . }
  OPTIONAL { ?col gv:hasTag / gv:name ?tagName . }
}
GROUP BY ?column ?table ?columnName
ORDER BY ?column
"""


def sensitive_columns():
    require_estate()
    _, rows = sparql(QUERY)
    for row in rows:
        have = set(filter(None, row.get("hasTags", "").split(", ")))
        want = set(filter(None, row.get("expected", "").split(", ")))
        row["hasTags"] = ", ".join(sorted(have))
        row["missingTags"] = sorted(want - have)
        row["missing"] = bool(row["missingTags"])
    return rows
