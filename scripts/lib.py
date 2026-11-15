"""Small helpers shared by the demo scripts. Python standard library only."""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAVITINO = os.environ.get("GRAVITINO_URL", "http://gravitino:8090")
FUSEKI = os.environ.get("FUSEKI_URL", "http://fuseki:3030/acme")
METALAKE = os.environ.get("METALAKE", "acme")
CATALOG = os.environ.get("CATALOG", "lakehouse")

GRAPH_ONTOLOGY = "urn:graph:ontology"
GRAPH_LINKS = "urn:graph:links"
GRAPH_ESTATE = "urn:graph:estate"

GRAVITINO_HEADERS = {
    "Accept": "application/vnd.gravitino.v1+json",
    "Content-Type": "application/json",
}


def _request(method, url, body=None, headers=None):
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else body.encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as err:
        host = urllib.parse.urlsplit(url).netloc
        raise SystemExit(f"Cannot reach {host} ({getattr(err, 'reason', err)}). "
                         "Is the stack up? Check: docker compose ps -a")


# --------------------------------------------------------------------------- Gravitino

def gravitino(method, path, payload=None, ok=(200,)):
    """Call the Gravitino REST API. path starts after /api, e.g. /metalakes."""
    body = json.dumps(payload) if payload is not None else None
    status, text = _request(method, GRAVITINO + "/api" + path, body, GRAVITINO_HEADERS)
    result = json.loads(text) if text else {}
    if status not in ok:
        raise RuntimeError(f"Gravitino {method} {path} -> HTTP {status}: {text}")
    return status, result


def wait_for(url, name, seconds=300):
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            status, _ = _request("GET", url)
            if status < 500:
                return
        except SystemExit:
            pass
        time.sleep(3)
    sys.exit(f"{name} did not come up at {url}")


def column_tags(table_path, column):
    """Tag names on one column, e.g. column_tags('lakehouse.sales.orders', 'card')."""
    full = f"{table_path}.{column}"
    _, res = gravitino("GET", f"/metalakes/{METALAKE}/objects/column/{full}/tags")
    return sorted(res.get("names", []))


def tag_column(table_path, column, tags):
    full = f"{table_path}.{column}"
    gravitino("POST", f"/metalakes/{METALAKE}/objects/column/{full}/tags",
              {"tagsToAdd": list(tags), "tagsToRemove": []})


def ensure_tag(name, comment):
    status, _ = gravitino("POST", f"/metalakes/{METALAKE}/tags",
                          {"name": name, "comment": comment, "properties": {}},
                          ok=(200, 409))
    return status == 200


# --------------------------------------------------------------------------- Fuseki

def put_graph(graph, turtle):
    """Replace one named graph in Fuseki with the given Turtle text."""
    url = FUSEKI + "/data?graph=" + urllib.parse.quote(graph, safe="")
    status, text = _request("PUT", url, turtle, {"Content-Type": "text/turtle; charset=utf-8"})
    if status not in (200, 201, 204):
        raise RuntimeError(f"Fuseki PUT {graph} -> HTTP {status}: {text}")


def sparql(query):
    """Run a SPARQL SELECT and return a list of dicts, one per result row."""
    body = urllib.parse.urlencode({"query": query})
    status, text = _request("POST", FUSEKI + "/sparql", body, {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/sparql-results+json",
    })
    if status != 200:
        raise RuntimeError(f"SPARQL failed, HTTP {status}: {text}")
    res = json.loads(text)
    rows = []
    for binding in res["results"]["bindings"]:
        rows.append({k: v["value"] for k, v in binding.items()})
    return res["head"]["vars"], rows


def require_estate():
    """Stop with a clear message if the mirrored estate is not in Fuseki yet."""
    _, rows = sparql("PREFIX gv: <http://example.org/gravitino#> "
                     "SELECT (COUNT(?c) AS ?n) WHERE { ?c a gv:Column }")
    if not rows or rows[0].get("n", "0") == "0":
        sys.exit("The Gravitino estate is not in Fuseki yet. The sample is still loading "
                 "or failed;\ncheck with: docker compose logs init init-tables init-estate")


PREFIXES = {
    "http://example.org/acme#": "acme:",
    "http://example.org/gravitino#": "gv:",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
    "http://www.w3.org/2002/07/owl#": "owl:",
    f"urn:gravitino:{METALAKE}:": "",
}


def short(value):
    for long_form, prefix in PREFIXES.items():
        if value.startswith(long_form):
            return prefix + value[len(long_form):]
    return value


def print_table(columns, rows):
    if not rows:
        print("(no rows)")
        return
    cells = [[short(r.get(c, "")) for c in columns] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells)) for i, c in enumerate(columns)]
    line = "  ".join(c.ljust(w) for c, w in zip(columns, widths))
    print(line)
    print("  ".join("-" * w for w in widths))
    for row in cells:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"\n{len(rows)} row(s)")
