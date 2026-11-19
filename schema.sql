-- PVR Cinema Operations & Staff Performance Database Schema

CREATE TABLE IF NOT EXISTS cinemas (
    cinema_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cinema_name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    total_screens INTEGER NOT NULL CHECK (total_screens > 0)
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_name TEXT NOT NULL,
    role TEXT NOT NULL,
    cinema_id INTEGER NOT NULL,
    shift_type TEXT NOT NULL CHECK (shift_type IN ('Morning', 'Afternoon', 'Evening', 'Night')),
    attendance_rate REAL NOT NULL DEFAULT 100.0 CHECK (attendance_rate >= 0 AND attendance_rate <= 100),
    audit_score REAL NOT NULL DEFAULT 90.0 CHECK (audit_score >= 0 AND audit_score <= 100),
    FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shows (
    show_id INTEGER PRIMARY KEY AUTOINCREMENT,
    show_date TEXT NOT NULL,
    cinema_id INTEGER NOT NULL,
    screen_number INTEGER NOT NULL CHECK (screen_number > 0),
    movie_title TEXT NOT NULL,
    show_slot TEXT NOT NULL CHECK (show_slot IN ('Morning', 'Matinee', 'Evening', 'Night')),
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    booked_seats INTEGER NOT NULL CHECK (booked_seats >= 0),
    ad_placement_verified INTEGER NOT NULL DEFAULT 1 CHECK (ad_placement_verified IN (0, 1)),
    av_quality_score REAL NOT NULL DEFAULT 95.0 CHECK (av_quality_score >= 0 AND av_quality_score <= 100),
    customer_rating REAL NOT NULL DEFAULT 4.2 CHECK (customer_rating >= 1.0 AND customer_rating <= 5.0),
    staff_id INTEGER,
    FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_shows_date ON shows(show_date);
CREATE INDEX IF NOT EXISTS idx_shows_slot ON shows(show_slot);
CREATE INDEX IF NOT EXISTS idx_shows_cinema ON shows(cinema_id);
