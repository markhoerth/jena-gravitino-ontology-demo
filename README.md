# Ontologies in practice: Apache Jena and Apache Gravitino

The exercise from the talk *Ontologies in Practice: Apache Jena and Apache Gravitino* (Mark Hoerth, Datastrato, November 2026). One Compose file brings up Apache Jena Fuseki with a small business ontology, Apache Gravitino serving Iceberg tables over its Iceberg REST catalog, and Apache Spark pointed at those tables.

It shows three things:

1. **Linking the ontology to the catalog.** A script copies the Gravitino estate into Jena, and a short hand-written file says which business concept lives in which column.
2. **Querying the ontology.** One SPARQL query finds every sensitive column, including ones nobody tagged, by walking the class hierarchy.
3. **Writing the answer back.** The ontology's answer becomes a `pci` tag on the column in Gravitino, and a check lists every sensitive column still missing its tag.

Everything here is Apache 2.0. See [LICENSE](LICENSE).

A personal example by Mark Hoerth, provided as is. Not an Apache Software Foundation project. Apache, Apache Gravitino, Apache Jena, Apache Iceberg and Apache Spark are trademarks of the Apache Software Foundation. Every version in the stack is pinned, and the whole stack is tested on Docker on Linux.

## Start from zero

You need nothing installed except Docker. These steps assume you have never used Docker or Git before. Allow about 20 minutes, most of it downloads.

### Step 1: Pick a machine

Any one of these works:

- **A Mac** (Intel or Apple silicon) with 8 GB of memory or more
- **A Windows 10 or 11 PC** with 8 GB of memory or more
- **A Linux machine or a cloud VM** with 2 CPUs, 8 GB of memory and 20 GB of disk, such as an AWS EC2 `t3.large` running Ubuntu

The stack uses about 4 GB of memory and 5 GB of disk.

### Step 2: Install Docker

**On a Mac:**

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/ and install it like any other app.
2. Open Docker Desktop and wait until it says Docker is running.
3. Open the **Terminal** app. Every command in this README goes there.

**On Windows:**

The commands in this README are Linux commands, so on Windows you run them inside WSL, a small Linux that Windows provides.

1. Open **PowerShell as Administrator** (right-click the Start button, then **Terminal (Admin)**) and run:
   ```
   wsl --install
   ```
   Restart the PC when it asks.
2. After the restart an **Ubuntu** window opens. Choose a user name and password when it asks. From now on, every command in this README goes in that Ubuntu window. You can reopen it any time from the Start menu by searching for **Ubuntu**.
3. Download Docker Desktop from https://www.docker.com/products/docker-desktop/ and install it.
4. Open Docker Desktop, go to **Settings → Resources → WSL integration**, switch on **Ubuntu**, and click **Apply & restart**.

**On Linux or a cloud VM (Ubuntu):**

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
exit
```

The last line logs you out. Log back in so your user can run Docker without `sudo`.

**Check Docker works (all machines):**

```bash
docker compose version
docker run --rm hello-world
```

The first line should print a version of v2.20 or later. The second should print `Hello from Docker!`.

### Step 3: Get the code

```bash
git clone https://github.com/markhoerth/jena-gravitino-ontology-demo
cd jena-gravitino-ontology-demo
```

If the first line says `git: command not found`, install Git and run it again: on a Mac run `xcode-select --install`; on Ubuntu or WSL run `sudo apt-get update && sudo apt-get install -y git`.

On Windows, clone inside the Ubuntu window, not in a Windows folder or with a Windows Git tool. The scripts are Linux scripts and stop working if Windows changes their line endings.

### Step 4: Start the stack

```bash
docker compose up -d
```

The first run downloads about 5 GB and builds two small images, so it takes 5 to 15 minutes depending on your connection. Later starts take under a minute. The command returns when every container has started; the sample keeps loading for about a minute after that.

To see where it is:

```bash
docker compose ps -a
```

When it is ready, `fuseki`, `gravitino`, `postgres` and `spark` show `running`, and `init`, `init-tables` and `init-estate` show `exited (0)`. Those three are one-shot jobs that load the sample and stop; `exited (0)` means they finished without error.

### Step 5: Run the first command

```bash
./find-sensitive
```

It waits for the sample to finish loading, then prints a table of 8 sensitive columns, followed by the 5 that nobody ever tagged. If you see that, everything works. Carry on with the three use cases below.

### What is running

| Service | What it is | Address |
|---|---|---|
| `fuseki` | Apache Jena Fuseki 6.2.0: SPARQL server and web UI | http://localhost:3030 (UI login: `admin` / `admin`) |
| `gravitino` | Apache Gravitino 1.3.1: catalog, REST API and web UI | http://localhost:8090 |
| | Gravitino's Iceberg REST catalog service | http://localhost:9001/iceberg/ |
| `spark` | Apache Spark 3.5.7 with Apache Iceberg 1.11.0 | `./spark-sql` |
| `postgres` | Where the Iceberg catalog keeps its table pointers | internal only |
| `init`, `init-tables`, `init-estate` | One-shot jobs that load the sample, then exit | |

The scripts run inside a Python container, so you do not need Python, Java or Spark on your machine.

On a Mac or Windows PC, open the addresses in your normal browser. Fuseki asks for a login: user `admin`, password `admin`. Gravitino asks for none. On a cloud VM, the addresses only work on the VM itself. To open them from your own computer, keep an SSH tunnel open in a terminal on your computer while you browse. Set the two variables to your key file and the VM's address:

```bash
KEY=~/.ssh/my-key.pem       # change to the key file you use to log in to the VM
VM=ubuntu@203.0.113.10      # change 203.0.113.10 to your VM's public IP address
ssh -i "$KEY" -L 3030:localhost:3030 -L 8090:localhost:8090 "$VM"
```

### If something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `address already in use` on port 3030, 8090 or 9001 | Something else on your machine uses that port | Find it with `sudo ss -ltnp \| grep -E ':3030\|:8090\|:9001'` (Linux, WSL) or `lsof -i :3030` (Mac), stop it, then run `docker compose up -d` again |
| `permission denied ... docker.sock` | Your user is not in the `docker` group yet | Log out and back in after Step 2, or on Mac and Windows check Docker Desktop is running |
| `Cannot connect to the Docker daemon` | Docker is not running | Start Docker Desktop, or on Linux run `sudo systemctl start docker` |
| `/usr/bin/env: 'bash\r': No such file or directory` | Windows changed the line endings | Delete the folder and clone again inside the Ubuntu window (Step 3) |
| `The sample has not been loaded` | The stack is not up | Run `docker compose up -d` |
| `The sample did not load` | One of the loading jobs failed | Run `docker compose logs init init-tables init-estate` and look at the last lines |
| A container keeps restarting, or the machine is very slow | Not enough memory for Docker | Give Docker at least 4 GB in Docker Desktop under **Settings → Resources**, or use a bigger VM |

## The sample

Acme has five Iceberg tables in a Gravitino metalake called `acme`, catalog `lakehouse`:

| Table | Columns |
|---|---|
| `crm.customers` | customer_id, full_name, email, phone, ssn, city |
| `sales.orders` | order_id, customer_id, **card**, amount, order_ts |
| `payments.refunds` | refund_id, order_id, **pan_7**, amount |
| `finance.accounts` | account_no, customer_id, balance, currency |
| `games.sessions` | session_id, player_id, **card_game_id**, score |

Some columns are already tagged, the way a real estate would be. Two teams tagged personal data and spelled it differently: `email` and `phone` carry `pii`, `ssn` carries `PII`. Nobody tagged either card number column. `card` holds card numbers under an obvious name, `pan_7` holds them under an obscure one, and `card_game_id` has "card" in its name but holds game identifiers.

```bash
./spark-sql "SELECT * FROM sales.orders"
```

The card numbers are standard test numbers.

## Use case 1: link the ontology to the catalog

Three pieces meet in one Jena store, each in its own named graph:

| Graph | File | Who writes it |
|---|---|---|
| `urn:graph:ontology` | [`ontology/acme.ttl`](ontology/acme.ttl) | You, by hand |
| `urn:graph:estate` | written by [`scripts/mirror.py`](scripts/mirror.py) | A script, from the Gravitino REST API |
| `urn:graph:links` | [`ontology/links.ttl`](ontology/links.ttl) | You, by hand |

**The ontology** (`acme.ttl`, about 60 lines of Turtle) knows nothing about tables. It says Payment card is a kind of Financial data, Financial data is a kind of Sensitive data, a Card number is Payment card data, and a Customer holds an Account. It also names the tag each category should carry: `pii`, `pci`, `financial`.

**The estate** is a copy of what Gravitino already knows: which schemas sit in which catalog, which columns sit in which table, which tags are on them. Run it yourself and look at what it writes:

```bash
./mirror --show
```

Every Gravitino object gets a name like `urn:gravitino:acme:lakehouse.sales.orders.card`. Nothing is invented. Every line is something Gravitino returned.

**The links** (`links.ttl`) join the two. A handful of lines say the Card number concept is stored in `sales.orders.card` and `payments.refunds.pan_7`, and that the Gravitino tags `pii` and `PII` both stand for the class Personal data. Without these lines the two graphs never meet. The join is declared, not guessed from column names.

To see the three graphs, open http://localhost:3030, log in as `admin` / `admin`, pick the `acme` dataset and run:

```sparql
SELECT ?g (COUNT(*) AS ?triples) WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g
```

Run `./mirror` again whenever tags change in Gravitino. The write-back in use case 3 does it for you.

## Use case 2: query the ontology

```bash
./find-sensitive
```

It returns eight columns. Five of them were never tagged by anyone: `card`, `pan_7`, `full_name`, `account_no` and `balance`. They are found because the ontology says what kind of data their concept is, and that kind rolls up to Sensitive data. `card_game_id` is not found, because its concept, Game identifier, is Operational data. No step matched on a column name.

The core of it is the query from slide 11:

```sparql
SELECT DISTINCT ?table WHERE {
  ?category rdfs:subClassOf* acme:SensitiveData .
  ?concept  acme:hasDataCategory ?category .
  ?concept  acme:storedIn        ?table .
}
```

`rdfs:subClassOf*` walks the "is a kind of" chain as far as it goes. Without the star, only categories declared directly under Sensitive data would match, and Payment card, two levels down, would be missed.

`./find-sensitive` adds a second road in: a column also counts if it carries a Gravitino tag that stands for a sensitive class. That is how `phone` is found. It has no link in `links.ttl`, only a `pii` tag.

More queries to run, each commented in its file:

```bash
./sparql queries/01-slide-11.rq          # the slide 11 query, unchanged
./sparql queries/02-category-tree.rq     # the ontology alone: every category and its parent
./sparql queries/03-explain-column.rq    # why is pan_7 sensitive? the whole chain, one row per step
./sparql queries/04-customer-data.rq     # "where is customer data?" following holds and places
./sparql queries/05-two-roads-in.rq      # found by link, found by tag, or both
```

You can also paste any of them into the query tab of the Fuseki UI, or pass a query inline:

```bash
./sparql 'PREFIX acme: <http://example.org/acme#> SELECT ?class ?tag WHERE { ?class acme:canonicalTag ?tag }'
```

Try editing `03-explain-column.rq` to ask about `card_game_id` instead of `pan_7`.

## Use case 3: write the answer back into Gravitino

Jena works out which columns are sensitive. Gravitino is where that fact needs to live, because Gravitino is where access is decided.

First, see what is missing:

```bash
./check-tags
```

Each sensitive column should carry the tag its category names in the ontology. Six do not: the five untagged columns, plus `ssn`, which carries the other team's `PII` instead of the canonical `pii`.

Fix the card column:

```bash
./write-back card
```

The script adds `pci` to `lakehouse.sales.orders.card` through the Gravitino REST API, reads the tags back from Gravitino to show they landed, and refreshes the copy in Jena. Ask Gravitino directly:

```bash
curl -s -H 'Accept: application/vnd.gravitino.v1+json' \
  http://localhost:8090/api/metalakes/acme/objects/column/lakehouse.sales.orders.card/tags
```

Run `./check-tags` again and `card` is gone from the list while `pan_7` is still there. Fix that one by name (`./write-back pan_7`) or everything at once (`./write-back --all`).

### Where the demo stops

Slide 12 continues: a policy on the `pci` tag masks the column, and the same Spark query returns `nnnn-nnnn-nnnn-1234`. Apache Gravitino 1.3.1 records the tag but does not mask a column in Spark, so this Compose file ends with the tag in Gravitino. Run the Spark query again after the write-back and the card numbers still come back in full:

```bash
./spark-sql "SELECT order_id, card FROM sales.orders"
```

The masked read needs an enforcement point that acts on the tag at query time. The ontology's part, deciding which columns get the tag, is complete here.

## Point it at your own Gravitino

The scripts read three settings:

```bash
export GRAVITINO_URL=http://my-gravitino.example.com:8090
export METALAKE=prod
./mirror
```

Then:

1. Replace `ontology/acme.ttl` with your own Turtle file, or extend it. Keep `acme:hasDataCategory`, `acme:storedIn`, `acme:standsFor` and `acme:canonicalTag`, or change the queries in `scripts/sensitive.py` to match your property names.
2. Rewrite `ontology/links.ttl` for your columns, using the names `./mirror --show` prints.
3. Reload the two hand-written files: `docker compose run --rm init` (it is safe to run again; it also creates the demo metalake and tags on whatever Gravitino it points at, so on a real server load the files by hand instead, as in `scripts/setup.py`).

`./write-back` writes tags into the Gravitino it points at. Run `./check-tags` first and read what it would change.

## Stop, reset, start over

```bash
docker compose down          # stop; data and tags are kept
docker compose up -d         # start again where you left off
docker compose down -v       # stop and delete everything; next up -d reloads the sample
```

## How it is wired

- **Gravitino** runs its Iceberg REST service with `dynamic-config-provider`, so the REST endpoint on port 9001 serves the `lakehouse` catalog defined in the metalake. Spark and Gravitino see the same tables because there is only one catalog definition.
- The Iceberg catalog uses the **JDBC backend** on Postgres, so table pointers survive restarts. The Postgres driver ships in the Gravitino image; [`gravitino/entrypoint.sh`](gravitino/entrypoint.sh) links it where the catalog loads it.
- Gravitino writes Iceberg metadata files and Spark writes data files into one shared volume, mounted at `/data/warehouse` in both containers. Gravitino runs as root so it can write there.
- **Fuseki** is built from the Apache release jar on Maven Central. It stores the dataset on disk (TDB2) with `unionDefaultGraph`, so a plain query sees all three named graphs at once. That is what lets one query start at an ontology class and end at a Gravitino column.
- The scripts use only the Python standard library and talk to both servers over plain HTTP: the Gravitino REST API, and the SPARQL and Graph Store endpoints of Fuseki.

## Files

```
docker-compose.yml        the stack
ontology/acme.ttl         the ontology (hand-written)
ontology/links.ttl        concept-to-column and tag-to-class links (hand-written)
queries/*.rq              five SPARQL queries to learn from
scripts/mirror.py         use case 1: Gravitino estate -> RDF in Fuseki
scripts/find_sensitive.py use case 2: which columns are sensitive
scripts/sensitive.py      the shared SPARQL query behind use cases 2 and 3
scripts/check_tags.py     use case 3: which sensitive columns lack their tag
scripts/write_back.py     use case 3: put the tag on the column in Gravitino
scripts/setup.py          creates the metalake, catalog and tags; loads the ontology
scripts/estate_tags.py    applies the tags the sample starts with
seed/seed.sql             the five tables and their rows (Spark SQL)
fuseki/  gravitino/  spark/   container config
```
