#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER postgres PASSWORD 'postgres';
	CREATE DATABASE telesend;
	GRANT ALL PRIVILEGES ON DATABASE telesend TO postgres;
EOSQL