#!/bin/bash
# Put the bundled Postgres JDBC driver where the Iceberg catalog and the
# Iceberg REST service can load it, then hand over to the image's own entrypoint.
set -e
cd /opt/gravitino
for dir in catalogs/lakehouse-iceberg/libs iceberg-rest-server/libs; do
  mkdir -p "$dir"
  ln -sf /opt/gravitino/jdbc-drivers/postgresql-*.jar "$dir/"
done
exec /bin/bash /opt/gravitino/docker/docker-entrypoint.sh
