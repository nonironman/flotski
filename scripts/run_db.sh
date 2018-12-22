#!/bin/bash

DB_USER=test
DB_PASS=test
DB_NAME=test
DB_PORT=5432

docker run  --name=flotski-db -p ${DB_PORT}:5432 \
            -e POSTGRES_USER=${DB_USER} \
            -e POSTGRES_PASSWORD=${DB_PASS} \
            -e POSTGRES_DB=${DB_NAME} \
            -d postgres:10-alpine