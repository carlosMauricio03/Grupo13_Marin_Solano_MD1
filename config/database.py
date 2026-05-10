import os
import psycopg2


def get_connection():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5433")

    # Docker service name "postgres" needs localhost mapping
    if host == "postgres":
        host = "localhost"
        port = "5433"

    # Local connections don't need SSL
    if host in ("localhost", "127.0.0.1"):
        sslmode = "disable"
    else:
        sslmode = "require"

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=sslmode
    )
