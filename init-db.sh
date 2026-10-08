#!/bin/bash
# ============================================================
# Script d'initialisation des bases de données PostgreSQL.
# Ce script est exécuté automatiquement au premier démarrage
# du conteneur PostgreSQL (via /docker-entrypoint-initdb.d/).
# ============================================================
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE votes_db;
    CREATE DATABASE notifications_db;
    GRANT ALL PRIVILEGES ON DATABASE votes_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE notifications_db TO $POSTGRES_USER;
EOSQL

echo "Bases de données créées : votes_db, notifications_db"
