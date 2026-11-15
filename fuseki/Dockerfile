# Apache Jena Fuseki, built straight from the Apache release on Maven Central.
FROM eclipse-temurin:21-jre

ARG JENA_VERSION=6.2.0
ADD https://repo1.maven.org/maven2/org/apache/jena/jena-fuseki-server/${JENA_VERSION}/jena-fuseki-server-${JENA_VERSION}.jar /fuseki/fuseki-server.jar
COPY config.ttl shiro.ini /fuseki/

WORKDIR /fuseki
EXPOSE 3030
CMD ["java", "-Xmx1g", "-jar", "/fuseki/fuseki-server.jar", "--shiro=/fuseki/shiro.ini", "--config=/fuseki/config.ttl"]
