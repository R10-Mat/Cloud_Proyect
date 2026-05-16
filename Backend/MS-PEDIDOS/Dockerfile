# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM maven:3.9.6-eclipse-temurin-17 AS builder

WORKDIR /app

# Copia el pom primero para cachear dependencias
COPY pom.xml .
RUN mvn dependency:go-offline -q

# Copia el código fuente y compila
COPY src ./src
RUN mvn clean package -DskipTests -q

# ── Stage 2: Runtime ───────────────────────────────────────────────────────────
FROM eclipse-temurin:17-jre

WORKDIR /app

# Copia solo el JAR generado
COPY --from=builder /app/target/ms-pedidos-1.0.0.jar app.jar

# Puerto interno del servicio
EXPOSE 8080

# Variables de entorno con valores por defecto (se sobreescriben en docker-compose)
ENV POSTGRES_HOST=postgres_pedidos \
    POSTGRES_PORT=5432 \
    POSTGRES_DB=pedidos_db \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

ENTRYPOINT ["java", "-jar", "app.jar"]
