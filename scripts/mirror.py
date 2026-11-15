"""Use case 1, part one: copy the Gravitino estate into Fuseki as RDF.

Walks the Gravitino REST API (metalake -> catalogs -> schemas -> tables ->
columns -> tags) and writes what it finds into the named graph urn:graph:estate.
Structure only. Nothing is invented: every triple is something Gravitino said.

Usage: ./mirror            (prints a summary)
       ./mirror --show     (also prints the Turtle it wrote)
"""

import sys

from lib import GRAPH_ESTATE, METALAKE, gravitino, put_graph

GV = "http://example.org/gravitino#"


def iri(*parts):
    return f"<urn:gravitino:{METALAKE}:{'.'.join(parts)}>"


def tag_iri(name):
    return f"<urn:gravitino:{METALAKE}:tag:{name}>"


def lit(text):
    return '"' + str(text).replace("\\", "\\\\").replace('"', '\\"') + '"'


lines = [f"@prefix gv: <{GV}> .", ""]
counts = {"catalogs": 0, "schemas": 0, "tables": 0, "columns": 0, "column tags": 0}
tag_names = set()

metalake = f"<urn:gravitino:{METALAKE}>"
lines.append(f"{metalake} a gv:Metalake ; gv:name {lit(METALAKE)} .")

_, res = gravitino("GET", f"/metalakes/{METALAKE}/catalogs?details=true")
for cat in res.get("catalogs", []):
    c = cat["name"]
    counts["catalogs"] += 1
    lines.append(f"{iri(c)} a gv:Catalog ; gv:name {lit(c)} ; gv:provider {lit(cat.get('provider', ''))} ;"
                 f" gv:inMetalake {metalake} .")
    if cat.get("type") != "relational":
        continue

    _, res = gravitino("GET", f"/metalakes/{METALAKE}/catalogs/{c}/schemas")
    for schema_ident in res.get("identifiers", []):
        s = schema_ident["name"]
        counts["schemas"] += 1
        lines.append(f"{iri(c, s)} a gv:Schema ; gv:name {lit(s)} ; gv:inCatalog {iri(c)} .")

        _, res_t = gravitino("GET", f"/metalakes/{METALAKE}/catalogs/{c}/schemas/{s}/tables")
        for table_ident in res_t.get("identifiers", []):
            t = table_ident["name"]
            counts["tables"] += 1
            lines.append(f"{iri(c, s, t)} a gv:Table ; gv:name {lit(t)} ; gv:inSchema {iri(c, s)} ;"
                         f" gv:fullName {lit(f'{c}.{s}.{t}')} .")

            _, table = gravitino("GET", f"/metalakes/{METALAKE}/catalogs/{c}/schemas/{s}/tables/{t}")
            for col in table["table"]["columns"]:
                name = col["name"]
                col_type = col["type"] if isinstance(col["type"], str) else col["type"].get("type", "complex")
                counts["columns"] += 1
                lines.append(f"{iri(c, s, t, name)} a gv:Column ; gv:name {lit(name)} ;"
                             f" gv:dataType {lit(col_type)} ; gv:inTable {iri(c, s, t)} ;"
                             f" gv:fullName {lit(f'{c}.{s}.{t}.{name}')} .")

                _, tags = gravitino("GET", f"/metalakes/{METALAKE}/objects/column/{c}.{s}.{t}.{name}/tags")
                for tag in tags.get("names", []):
                    counts["column tags"] += 1
                    tag_names.add(tag)
                    lines.append(f"{iri(c, s, t, name)} gv:hasTag {tag_iri(tag)} .")

for tag in sorted(tag_names):
    lines.append(f"{tag_iri(tag)} a gv:Tag ; gv:name {lit(tag)} .")

turtle = "\n".join(lines) + "\n"
put_graph(GRAPH_ESTATE, turtle)

if "--show" in sys.argv:
    print(turtle)
print("Mirrored Gravitino metalake '%s' into Fuseki graph %s" % (METALAKE, GRAPH_ESTATE))
print("  " + ", ".join(f"{v} {k}" for k, v in counts.items()))
