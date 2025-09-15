#!/bin/bash
# database_setup.sh
# This script downloads the Northwind sample database for PostgreSQL and sets up the database using Docker Compose.

set -e  # Exit immediately if a command exits with a non-zero status

# Step 1: Download the Northwind SQL file if it doesn't exist
NORTHWIND_SQL="./init/northwind.sql"
if [ ! -f "$NORTHWIND_SQL" ]; then
  echo "Downloading Northwind SQL file..."
  curl -L -o "$NORTHWIND_SQL" "https://raw.githubusercontent.com/pthom/northwind_psql/master/northwind.sql"
else
  echo "Northwind SQL file already exists."
fi

# Step 2: Start PostgreSQL using Docker Compose
# This will automatically run any .sql files in ./init (including northwind.sql)
echo "Starting PostgreSQL with Docker Compose..."
docker-compose up -d

echo "Database setup complete!"
