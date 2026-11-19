import tempfile
import unittest
from pathlib import Path

from analytics import get_dashboard_summary
from database import import_csv_text, insert_show_record
from seed_data import seed_database


class TestPVROperations(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test_pvr.db"
        self.seeded_count = seed_database(self.db_path)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_seed_and_summary(self) -> None:
        self.assertEqual(self.seeded_count, 10)
        summary = get_dashboard_summary(db_path=self.db_path)
        self.assertEqual(summary["kpis"]["total_shows"], 10)
        self.assertGreater(summary["kpis"]["avg_occupancy_pct"], 50.0)
        self.assertTrue(len(summary["slot_breakdown"]) > 0)

    def test_insert_and_csv_import(self) -> None:
        show_id = insert_show_record(
            {
                "show_date": "2025-11-05",
                "cinema_name": "PVR Priya",
                "movie_title": "Pushpa 2",
                "show_slot": "Evening",
                "total_seats": 300,
                "booked_seats": 270,
                "staff_name": "Nikhil Kumar",
            },
            db_path=self.db_path,
        )
        self.assertGreater(show_id, 0)
        csv_data = "show_date,cinema_name,movie_title,show_slot,total_seats,booked_seats\n2025-11-06,PVR Priya,Pushpa 2,Night,200,150\n"
        inserted = import_csv_text(csv_data, db_path=self.db_path)
        self.assertEqual(inserted, 1)
        summary = get_dashboard_summary(cinema_filter="PVR Priya", db_path=self.db_path)
        self.assertEqual(summary["kpis"]["total_shows"], 2)


if __name__ == "__main__":
    unittest.main()
