import csv
from pathlib import Path
from database import DB_PATH, import_csv_text, init_db

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_CSV_PATH = DATA_DIR / "sample_shows.csv"

SAMPLE_ROWS = [
    ["show_date", "cinema_name", "city", "total_screens", "screen_number", "movie_title", "show_slot", "total_seats", "booked_seats", "ad_placement_verified", "av_quality_score", "customer_rating", "staff_name", "staff_role", "shift_type", "attendance_rate", "audit_score"],
    ["2025-11-01", "PVR Select Citywalk", "New Delhi", "6", "1", "Singham Again", "Morning", "220", "132", "1", "96.5", "4.3", "Rohan Sharma", "Shift Supervisor", "Morning", "98.0", "95.0"],
    ["2025-11-01", "PVR Select Citywalk", "New Delhi", "6", "2", "Bhool Bhulaiyaa 3", "Matinee", "240", "198", "1", "98.0", "4.6", "Ananya Verma", "Floor QA Lead", "Afternoon", "97.5", "96.5"],
    ["2025-11-01", "PVR Select Citywalk", "New Delhi", "6", "3", "Singham Again", "Evening", "260", "247", "1", "99.0", "4.8", "Vikram Singh", "Senior Projectionist", "Evening", "99.0", "97.0"],
    ["2025-11-01", "PVR Select Citywalk", "New Delhi", "6", "4", "Venom: The Last Dance", "Night", "180", "126", "1", "95.0", "4.2", "Karan Mehta", "Night Shift Lead", "Night", "94.0", "91.0"],
    ["2025-11-02", "PVR Vegas Dwarka", "New Delhi", "12", "1", "Bhool Bhulaiyaa 3", "Morning", "250", "145", "1", "94.0", "4.1", "Pooja Nair", "Shift Supervisor", "Morning", "96.0", "93.0"],
    ["2025-11-02", "PVR Vegas Dwarka", "New Delhi", "12", "5", "Singham Again", "Evening", "300", "285", "1", "98.5", "4.7", "Amit Tiwari", "Floor QA Lead", "Evening", "98.5", "96.0"],
    ["2025-11-02", "PVR Vegas Dwarka", "New Delhi", "12", "8", "Amaran", "Night", "200", "164", "0", "92.0", "4.0", "Deepak Joshi", "Night Shift Lead", "Night", "92.5", "89.0"],
    ["2025-11-03", "PVR Ambience Mall", "Gurugram", "9", "2", "Bhool Bhulaiyaa 3", "Matinee", "220", "176", "1", "97.0", "4.5", "Neha Kapoor", "Floor QA Lead", "Afternoon", "97.0", "95.5"],
    ["2025-11-03", "PVR Ambience Mall", "Gurugram", "9", "4", "Singham Again", "Evening", "280", "266", "1", "99.2", "4.9", "Siddharth Rao", "Senior Projectionist", "Evening", "99.5", "98.0"],
    ["2025-11-03", "PVR Ambience Mall", "Gurugram", "9", "6", "Venom: The Last Dance", "Night", "190", "133", "1", "95.5", "4.3", "Rajesh Kumar", "Night Shift Lead", "Night", "95.0", "92.0"],
]


def ensure_sample_csv() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAMPLE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(SAMPLE_ROWS)
    return SAMPLE_CSV_PATH


def seed_database(db_path: Path = DB_PATH) -> int:
    init_db(db_path)
    csv_path = ensure_sample_csv()
    csv_text = csv_path.read_text(encoding="utf-8")
    return import_csv_text(csv_text, db_path=db_path)


if __name__ == "__main__":
    if DB_PATH.exists():
        DB_PATH.unlink()
    count = seed_database()
    print(f"Seeded {count} show records into {DB_PATH.name}")
