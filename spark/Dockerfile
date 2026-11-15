# Apache Spark with the Apache Iceberg runtime, pointed at Gravitino's Iceberg REST catalog.
FROM apache/spark:3.5.7-java17

ARG ICEBERG_VERSION=1.11.0
USER root
ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar /opt/spark/jars/
RUN chmod 644 /opt/spark/jars/iceberg-spark-runtime-*.jar
COPY spark-defaults.conf /opt/spark/conf/spark-defaults.conf
COPY log4j2.properties /opt/spark/conf/log4j2.properties
ENV PATH="/opt/spark/bin:${PATH}"
