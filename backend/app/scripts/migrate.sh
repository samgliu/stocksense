#!/bin/bash
docker-compose run --rm backend alembic "$@"
