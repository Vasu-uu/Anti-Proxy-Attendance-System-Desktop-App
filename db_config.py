import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu2005",
    "database": "Attandance"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
