#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER general_reader WITH PASSWORD 'general_reader' IN GROUP pg_read_all_data;
EOSQL
