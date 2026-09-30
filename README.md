# FastAPI CRUD con PostgreSQL, Alembic y AWS S3

API RESTful desarrollada con FastAPI, SQLModel, PostgreSQL, Alembic para migraciones y AWS S3 para la gestión de imágenes. Todo empaquetado en contenedores Docker gestionados mediante Docker Compose.

---

## Estructura del Proyecto

```text
FastApi_Luigui/
├── alembic/                      # Archivos de migración de la base de datos
│   ├── versions/                 # Scripts de migraciones individuales
│   │   ├── fd46bdcc99d0_first_migration.py
│   │   ├── d34b82694cc1_add_category_field_in_product_model.py
│   │   └── a1b2c3d4e5f6_add_images_s3_table.py
│   └── env.py                    # Configuración del entorno de Alembic
├── src/                          # Código fuente de la aplicación
│   ├── models/                   # Modelos de datos (SQLModel / Pydantic)
│   │   └── product_model.py
│   └── shared/                   # Módulos compartidos y configuración
│       └── database/
│           └── session_db.py     # Sesión y conexión a PostgreSQL
├── .dockerignore                 # Archivos excluidos en la construcción Docker
├── .env                          # Variables de entorno (Credenciales / Configuración)
├── .env.example                  # Plantilla de ejemplo para el .env
├── .gitignore                    # Archivos ignorados por Git
├── alembic.ini                   # Archivo de configuración global de Alembic
├── docker-compose.yml            # Orquestación de servicios (App + PostgreSQL)
├── Dockerfile                    # Construcción multi-stage de la imagen Docker
├── entrypoint.sh                 # Script de arranque del contenedor (Migraciones + Uvicorn)
├── main.py                       # Punto de entrada y definición de endpoints FastAPI
├── pyproject.toml                # Gestión de dependencias con uv
└── README.md                     # Documentación oficial del proyecto
```

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
* Docker Desktop (con Docker Engine y Docker Compose habilitados).
* Git (opcional, para clonar el repositorio).

---

## Configuración Paso a Paso

### 1. Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto tomando como base la plantilla `.env.example`. Modifica los valores con tus propias credenciales:

```env
# Conexión a la Base de Datos (Host 'db' es el servicio de Docker)
DATABASE_URL=postgresql://<tu_usuario>:<tu_contraseña>@db:5432/<nombre_bd>

# Credenciales de PostgreSQL
DB_USER=<tu_usuario>
DB_PASSWORD=<tu_contraseña>
DB_NAME=<nombre_bd>
DB_HOST=db
DB_PORT=5432

# Configuración de AWS / S3 para imágenes
AWS_BUCKET_NAME=<nombre_de_tu_bucket>
AWS_REGION=<tu_region_aws>
AWS_ACCESS_KEY_ID=<tu_access_key>
AWS_SECRET_ACCESS_KEY=<tu_secret_key>
```

> [!NOTE]
> * `db` es el nombre del servicio de la base de datos dentro de la red interna de Docker Compose.
> * Si ejecutas la aplicación dentro de una instancia AWS EC2 con un rol IAM adjunto, puedes dejar `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` vacías.

---

## Ejecución de la Aplicación

### Paso 1: Iniciar los contenedores

Ejecuta el siguiente comando en tu terminal dentro del directorio del proyecto:

```bash
docker compose up -d --build
```

Esto realizará las siguientes acciones automáticamente:
1. Construirá la imagen de FastAPI (`fastapi_app`).
2. Descargará e iniciará el contenedor de PostgreSQL 16 (`fastapi_db`).
3. Mapeará el puerto `5432` para acceso externo desde tu máquina local (DBeaver, pgAdmin, etc.).
4. Mapeará el puerto `8000` para acceder a la API.
5. Ejecutará automáticamente las migraciones pendientes de Alembic (`alembic upgrade head`) antes de iniciar la aplicación.

---

### Paso 2: Verificar el estado de los servicios

Comprueba que ambos contenedores estén corriendo y en estado healthy:

```bash
docker ps
```

Deberías ver una salida similar a:

| CONTAINER ID | IMAGE | STATUS | PORTS | NAMES |
| :--- | :--- | :--- | :--- | :--- |
| `<container_id>` | `postgres:16` | Up (healthy) | `0.0.0.0:5432->5432/tcp` | `fastapi_db` |
| `<container_id>` | `fastapi_luigui-web` | Up (healthy) | `0.0.0.0:8000->8000/tcp` | `fastapi_app` |

---

## Acceso a la Documentación y API

* Documentación Interactiva (Swagger UI): http://localhost:8000/docs
* Documentación Alternativa (ReDoc): http://localhost:8000/redoc
* Health Check (Estado de la API): http://localhost:8000/health

---

## Conexión a la Base de Datos desde tu Máquina

Puedes conectar cualquier cliente visual de SQL (DBeaver, pgAdmin, TablePlus) usando los siguientes datos de conexión:

* Host: `localhost` o `127.0.0.1`
* Puerto: `5432`
* Base de Datos (`Database`): El valor configurado en `DB_NAME` en tu `.env`
* Usuario (`User`): El valor configurado en `DB_USER` en tu `.env`
* Contraseña (`Password`): El valor configurado en `DB_PASSWORD` en tu `.env`

---

## Comandos Útiles de Mantenimiento

### Ver logs en tiempo real:
```bash
docker compose logs -f
```

### Ejecutar migraciones manualmente:
```bash
docker exec fastapi_app alembic upgrade head
```

### Crear una nueva migración cuando modifiques un modelo:
```bash
docker exec fastapi_app alembic revision --autogenerate -m "descripcion_de_cambios"
```

### Detener los servicios:
```bash
docker compose down
```

### Detener y eliminar los volúmenes de datos (reset completo de BD):
```bash
docker compose down -v
```
