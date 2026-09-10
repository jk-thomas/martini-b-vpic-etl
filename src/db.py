"""
One table, one row per (make_id, model_id, model_year)
"one row per year + make + model" and keeps vPIC's own IDs
"""
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicle_models (
    make_id     INTEGER NOT NULL,
    make_name   TEXT    NOT NULL,
    model_id    INTEGER NOT NULL,
    model_name  TEXT    NOT NULL,
    model_year  INTEGER NOT NULL,
    updated_at  TEXT    NOT NULL,
    PRIMARY KEY (make_id, model_id, model_year)
);
"""

def open_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

def upsert_rows(conn, rows):
    inserted = 0
    updated = 0
    unchanged = 0

    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()

    for row in rows:
        cursor.execute(
            "SELECT model_name, make_name FROM vehicle_models "
            "WHERE make_id=? AND model_id=? AND model_year=?",
            (row["make_id"], row["model_id"], row["year"]),
        )
        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                "INSERT INTO vehicle_models (make_id, make_name, model_id, model_name, model_year, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (row["make_id"], row["make_name"], row["model_id"], row["model_name"], row["year"], now),
            )
            inserted += 1
        elif existing != (row["model_name"], row["make_name"]):
            cursor.execute(
                "UPDATE vehicle_models SET model_name=?, make_name=?, updated_at=? "
                "WHERE make_id=? AND model_id=? AND model_year=?",
                (row["model_name"], row["make_name"], now, row["make_id"], row["model_id"], row["year"]),
            )
            updated += 1
        else:
            unchanged += 1

    conn.commit()

    return {"inserted": inserted, "updated": updated, "unchanged": unchanged}
