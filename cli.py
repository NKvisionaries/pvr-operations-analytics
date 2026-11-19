import argparse
import json
from pathlib import Path

from analytics import get_dashboard_summary
from database import DB_PATH, import_csv_text, init_db
from seed_data import seed_database

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="PVR Cinema Operations & Staff Analytics CLI")
    parser.add_argument("--seed", action="store_true", help="Initialize and seed SQLite database with sample data")
    parser.add_argument("--import-csv", type=str, help="Path to a custom CSV file to import into SQLite")
    parser.add_argument("--cinema", type=str, default="", help="Filter summary by cinema name")
    parser.add_argument("--slot", type=str, default="", help="Filter summary by show slot")
    parser.add_argument("--summary", action="store_true", help="Print JSON analytics summary")
    args = parser.parse_args()

    if args.seed:
        count = seed_database(DB_PATH)
        print(f"Seeded {count} show records into {DB_PATH.name}")

    if args.import_csv:
        init_db(DB_PATH)
        csv_text = Path(args.import_csv).read_text(encoding="utf-8")
        count = import_csv_text(csv_text, DB_PATH)
        print(f"Imported {count} records from {args.import_csv}")

    if args.summary or (not args.seed and not args.import_csv):
        if not DB_PATH.exists():
            seed_database(DB_PATH)
        summary = get_dashboard_summary(cinema_filter=args.cinema, slot_filter=args.slot, db_path=DB_PATH)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
