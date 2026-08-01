# Nexa Commerce - catalog service (Java / Jakarta Servlet).
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn -q -B -DskipTests package

FROM tomcat:10.1-jre17-temurin
COPY --from=build /build/target/catalog.war /usr/local/tomcat/webapps/catalog.war

# USER is set deliberately: a missing USER instruction rates High in the
# reference tenant, and every chain in this repository must stay at
# Medium or below.
USER 10001

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fsS http://127.0.0.1:8080/catalog/ || exit 1
CMD ["catalina.sh", "run"]
