import csv
import io
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pvr_operations.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)


def get_or_create_cinema(conn: sqlite3.Connection, cinema_name: str, city: str = "New Delhi", total_screens: int = 6) -> int:
    row = conn.execute("SELECT cinema_id FROM cinemas WHERE cinema_name = ?", (cinema_name.strip(),)).fetchone()
    if row:
        return int(row["cinema_id"])
    cur = conn.execute(
        "INSERT INTO cinemas (cinema_name, city, total_screens) VALUES (?, ?, ?)",
        (cinema_name.strip(), city.strip() or "New Delhi", max(1, int(total_screens))),
    )
    return int(cur.lastrowid)


def get_or_create_staff(
    conn: sqlite3.Connection,
    staff_name: str,
    cinema_id: int,
    role: str = "Floor QA & Shift Lead",
    shift_type: str = "Evening",
    attendance_rate: float = 96.0,
    audit_score: float = 92.0,
) -> int:
    row = conn.execute(
        "SELECT staff_id FROM staff WHERE staff_name = ? AND cinema_id = ?",
        (staff_name.strip(), cinema_id),
    ).fetchone()
    if row:
        return int(row["staff_id"])
    valid_shift = shift_type if shift_type in ("Morning", "Afternoon", "Evening", "Night") else "Evening"
    cur = conn.execute(
        """
        INSERT INTO staff (staff_name, role, cinema_id, shift_type, attendance_rate, audit_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (staff_name.strip(), role.strip(), cinema_id, valid_shift, float(attendance_rate), float(audit_score)),
    )
    return int(cur.lastrowid)


def insert_show_record(record: dict, db_path: Path = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cinema_id = get_or_create_cinema(
            conn,
            record.get("cinema_name", "PVR Select Citywalk"),
            record.get("city", "New Delhi"),
            int(record.get("total_screens", 6)),
        )
        staff_id = None
        if record.get("staff_name"):
            staff_id = get_or_create_staff(
                conn,
                record["staff_name"],
                cinema_id,
                record.get("staff_role", "Shift Supervisor"),
                record.get("shift_type", "Evening"),
                float(record.get("attendance_rate", 95.0)),
                float(record.get("audit_score", 92.0)),
            )

        total_seats = max(1, int(record["total_seats"]))
        booked_seats = max(0, min(total_seats, int(record["booked_seats"])))
        show_slot = record.get("show_slot", "Evening")
        if show_slot not in ("Morning", "Matinee", "Evening", "Night"):
            show_slot = "Evening"

        cur = conn.execute(
            """
            INSERT INTO shows (
                show_date, cinema_id, screen_number, movie_title, show_slot,
                total_seats, booked_seats, ad_placement_verified, av_quality_score,
                customer_rating, staff_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record["show_date"]).strip(),
                cinema_id,
                max(1, int(record.get("screen_number", 1))),
                str(record["movie_title"]).strip(),
                show_slot,
                total_seats,
                booked_seats,
                1 if str(record.get("ad_placement_verified", 1)).strip().lower() in ("1", "true", "yes") else 0,
                min(100.0, max(0.0, float(record.get("av_quality_score", 95.0)))),
                min(5.0, max(1.0, float(record.get("customer_rating", 4.2)))),
                staff_id,
            ),
        )
        return int(cur.lastrowid)


def import_csv_text(csv_text: str, db_path: Path = DB_PATH) -> int:
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    inserted = 0
    for row in reader:
        if not row.get("show_date") or not row.get("movie_title"):
            continue
        insert_show_record(row, db_path=db_path)
        inserted += 1
    return inserted
