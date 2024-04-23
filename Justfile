default:
    just --list

up *args:
    @docker compose -f ./docker/docker-compose.yml up -d --build
    @if [ "{{args}}" = "-l" ]; then \
        docker logs app -f ;\
    fi

down:
    docker compose -f ./docker/docker-compose.yml down

kill:
    docker compose -f ./docker/docker-compose.yml kill

ps:
    docker compose -f ./docker/docker-compose.yml ps

logs *args:
    docker compose -f ./docker/docker-compose.yml logs {{args}} -f

exec *args:
    docker compose -f ./docker/docker-compose.yml exec app {{args}}

mm *args:
    docker compose -f ./docker/docker-compose.yml exec app alembic revision --autogenerate -m "{{args}}"

migrate:
    docker compose -f ./docker/docker-compose.yml exec app alembic upgrade head

downgrade *args:
    docker compose -f ./docker/docker-compose.yml exec app alembic downgrade {{args}}

ruff *args:
    docker compose -f ./docker/docker-compose.yml exec app ruff {{args}} src
    docker compose -f ./docker/docker-compose.yml exec app ruff format src

lint:
    docker compose -f ./docker/docker-compose.yml exec app just ruff --fix

mypy:
    docker compose -f ./docker/docker-compose.yml exec app mypy ./src/main.py

backup:
    docker compose -f ./docker/docker-compose.yml exec app_db scripts/backup

mount-docker-backup *args:
    docker cp app_db:/backups/{{args}} ./{{args}}

restore *args:
    docker compose -f ./docker/docker-compose.yml exec app_db scripts/restore {{args}}

remigrate:
    docker compose -f ./docker/docker-compose.yml exec app alembic downgrade base
    rm ./alembic/versions/*.py
    docker compose -f ./docker/docker-compose.yml exec app alembic revision --autogenerate -m init
    docker compose -f ./docker/docker-compose.yml exec app alembic upgrade head
