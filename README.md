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

## Justfile

The project uses [Just](https://github.com/casey/just) for command automation and ease of access. A better alternative to Makefile.

All shortucts are located in `justfile` in root directory. To view the commands you can also do:

```shell
just -l
```

Info about installation can be found [here](https://github.com/casey/just#packages).

## Local Development

Make sure to have `just` installed on you system and run for complete setup:

```
cat .env.example > .env
just setup
```
