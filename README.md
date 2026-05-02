# 🗄️ Infraestructura de Capa de Datos (Persistence Layer)

Este directorio contiene exclusivamente la configuración necesaria para desplegar los motores de base de datos del proyecto Last Mile.

## 🎯 Propósito de esta Rama

Esta rama ha sido optimizada para ser clonada **únicamente** en la máquina virtual destinada a la gestión y almacenamiento de datos (VM3). Su diseño permite un despliegue rápido, limpio y ligero de la infraestructura de persistencia.

## 🧠 Fundamentación Técnica

La decisión de aislar esta configuración y eliminar los archivos de aplicación se basa en los siguientes principios de arquitectura Cloud y DevOps:

### 1. Separación de Responsabilidades (SoC)
Al desacoplar la base de datos del código de aplicación, permitimos que la infraestructura de datos sea completamente independiente. Esto facilita el mantenimiento, las actualizaciones de versiones de BDs y la realización de backups sin afectar o depender del ciclo de vida del código (CI/CD) de los microservicios.

### 2. Eficiencia de Recursos (Lightweight Environment)
Al eliminar el código fuente, dependencias Node/Python/Java, y artefactos de construcción de los microservicios, garantizamos un entorno "lean". Esto asegura que la instancia de base de datos tenga el máximo de RAM, CPU y almacenamiento disponible dedicado **exclusivamente** al rendimiento de los motores de DB (MySQL, PostgreSQL y MongoDB).

### 3. Arquitectura de Red y Seguridad
La comunicación entre las máquinas virtuales de aplicación (encargadas de la lógica de negocio en VM1/VM2) y esta máquina de datos (VM3) se realiza a través de la red privada de nuestra VPC en AWS.

*   **Seguridad Inquebrantable:** El tráfico de datos es 100% interno. Los puertos de las bases de datos (3306, 5432, 27017) no se exponen a la internet pública, reduciendo drásticamente la superficie de ataque.
*   **Baja Latencia:** El uso de IPs privadas dentro de la misma región (y preferiblemente la misma Availability Zone) garantiza una conexión ultrarrápida y sin costos de transferencia de datos sobre internet.

## 🚀 Despliegue

Para desplegar esta capa de datos en la VM3, asegúrate de tener el archivo `.env` configurado correctamente con las contraseñas y luego ejecuta:

```bash
docker compose -f docker-compose-db.yml up -d
```
