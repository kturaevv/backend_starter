# CORE API

#### TODO:

- [x] Base code architecture
- [x] Static typing - Mypy
- [x] Raw SQL queries with psycopg3
- [x] Alembic migrations
- [x] Integration tests starter pack
- [x] Auth service - Custom
- [ ] Auth service - SuperTokens / KeyCloak?
- [ ] Traces - OpenTelemetry
- [ ] Observability - Prometheus + Grafana
- [ ] Payment service - Stripe
- [ ] Management - CRUD -> DB-service
- [ ] Statistics - CRUD -> DB-service
- [ ] Storage service - AWS
- [ ] Provisioning IaaC - Terraform on AWS EC2 / Fargate
- [ ] CI/CD Github Actions [managed]
- [ ] Reverse proxy - NGINX

## Pre-requisites

1. Make sure to have `just` installed on your system.
2. Make sure to have `Docker` installed on your system.
3. Copy environemnt variables to .env

```bash
cat .env.example > .env
```

4. Do migrations:

   - To start a project it is necessary to run migration scripts beforehand. One command will do the job:

   ```bash
   just migrate
   ```

   - If _./alembic/scripts_ folder is empty then you need to run migrations **before** migrate:

   ```bash
   just mm <initial migration name>
   ```

   - There is also a utility command to completely wipe all migrations and start from clean slate:

   ```bash
   just remigrate`
   ```

## Justfile

The project uses [Just](https://github.com/casey/just) for command automation and ease of access. A better alternative to Makefile.

All shortucts are located in `justfile` in root directory. To view the commands you can also do:

```shell
just -l
```

Info about installation can be found [here](https://github.com/casey/just#packages).

## Development

The project extensively uses Docker and Docker compose for development. To avoid local setup it is recommended to use `devcontainers` in vscode. It will open up VSCode instance within a development container and will contain all necessary packages for operation, contribution and tests.

To enter devcontainers follow these steps:

- Open VSCode instance at the root of the project
- Install recommended extensions
- Open VSCode command pallete with `ctrl + shift + key`
- Find **Dev Containers: Reopen in Container** option

With development setup containers are mounted to local filesystem, therefore containers and local files are always up to date! This makes utility commands defined in `Justfile` instrumental for efficient workflow. They work directly with running containers, thus the changes are always relevant.

_Note: It also possible to work without devcontainers. However, in order to support mypy annotations and warnings it will be required to setup a virtual environment._

## Project-wide decisions

### Project key points

- Strict integration of `mypy`.
- Excessive usage of Pydantic for data validation
- Usage of `psycopg3` for all database operations
- Usage of **pure** sql strings for CRUD
- Usage of Sqlalchemy2 only for migrations, table definition and pydantic support

### Project structure

Root level files:

- `src/` - highest level of an app, for common models, configs, and constants, etc.
- `src/main.py` - root of the project, which inits the FastAPI app
- `src/<file.py>` - global, project wide files and configs. For example, database.py for DB configs.

Each module is located in its own dedicated folder with common to files across modules:

- `router.py` - for endpoints
- `schemas.py` - for Pydantic schemas
- `models.py` - for db models
- `dependencies.py` - for router dependencies
- `service.py` - for business logic
- `constants.py` - constants and error codes
- `config.py` - module specific configurations
- `exceptions.py` - module specific exceptions
- `utils.py` - other
