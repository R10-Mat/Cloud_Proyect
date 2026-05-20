FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -q

COPY src ./src
RUN mvn clean package -DskipTests -q

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /app/target/ms-pedidos-1.0.0.jar app.jar

EXPOSE 8080

ENV POSTGRES_HOST=postgres_pedidos \
    POSTGRES_PORT=5432 \
    POSTGRES_DB=pedidos_db \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

ENTRYPOINT ["java", "-jar", "app.jar"]
