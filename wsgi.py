import json
from pathlib import Path
from urllib.parse import parse_qs

from analytics import get_dashboard_summary
from database import DB_PATH, import_csv_text, insert_show_record
from seed_data import SAMPLE_CSV_PATH, seed_database

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "static" / "index.html"


def ensure_db() -> None:
    if not DB_PATH.exists():
        seed_database(DB_PATH)


def application(environ, start_response):
    ensure_db()
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "GET" and path == "/":
        body = INDEX_HTML.read_bytes()
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [body]

    if method == "GET" and path == "/api/dashboard":
        qs = parse_qs(environ.get("QUERY_STRING", ""))
        data = get_dashboard_summary(
            cinema_filter=qs.get("cinema", [""])[0],
            slot_filter=qs.get("slot", [""])[0],
            db_path=DB_PATH,
        )
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(data).encode("utf-8")]

    if method == "GET" and path == "/api/template":
        body = SAMPLE_CSV_PATH.read_bytes()
        start_response(
            "200 OK",
            [
                ("Content-Type", "text/csv"),
                ("Content-Disposition", "attachment; filename=pvr_sample_template.csv"),
            ],
        )
        return [body]

    if method == "POST" and path == "/api/shows":
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(length).decode("utf-8")
        show_id = insert_show_record(json.loads(raw), db_path=DB_PATH)
        res = {"status": "ok", "show_id": show_id, "message": f"Saved show #{show_id}"}
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(res).encode("utf-8")]

    if method == "POST" and path == "/api/upload-csv":
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(length).decode("utf-8")
        count = import_csv_text(raw, db_path=DB_PATH)
        res = {"status": "ok", "inserted": count}
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(res).encode("utf-8")]

    start_response("404 Not Found", [("Content-Type", "application/json")])
    return [b'{"error": "Not found"}']
