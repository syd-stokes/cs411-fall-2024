#!/bin/bash

# Path to the database file
DB_PATH=${DB_PATH:-/app/data/movies.db}  # Default path if $DB_PATH is not set
SQL_FILE="./create_movie_table.sql"

# Check if the SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo "SQL file $SQL_FILE not found!"
    exit 1
fi

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Drop and recreate the tables
    sqlite3 "$DB_PATH" < "$SQL_FILE"
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    # Create the database for the first time
    sqlite3 "$DB_PATH" < "$SQL_FILE"
    echo "Database created successfully."
fi
