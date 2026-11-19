from pathlib import Path
from database import DB_PATH, get_connection


def get_dashboard_summary(cinema_filter: str = "", slot_filter: str = "", db_path: Path = DB_PATH) -> dict:
    where_clauses = []
    params = []
    if cinema_filter:
        where_clauses.append("c.cinema_name = ?")
        params.append(cinema_filter)
    if slot_filter:
        where_clauses.append("s.show_slot = ?")
        params.append(slot_filter)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection(db_path) as conn:
        kpis = conn.execute(
            f"""
            SELECT
                COUNT(s.show_id) AS total_shows,
                COALESCE(SUM(s.booked_seats), 0) AS total_booked,
                COALESCE(SUM(s.total_seats), 0) AS total_capacity,
                ROUND(COALESCE(AVG(CAST(s.booked_seats AS FLOAT) / s.total_seats * 100.0), 0), 2) AS avg_occupancy_pct,
                ROUND(COALESCE(AVG(s.ad_placement_verified) * 100.0, 0), 2) AS ad_compliance_pct,
                ROUND(COALESCE(AVG(s.av_quality_score), 0), 2) AS avg_av_quality,
                ROUND(COALESCE(AVG(s.customer_rating), 0), 2) AS avg_rating
            FROM shows s
            JOIN cinemas c ON s.cinema_id = c.cinema_id
            {where_sql}
            """,
            params,
        ).fetchone()

        slot_breakdown = [
            dict(r)
            for r in conn.execute(
                f"""
                SELECT
                    s.show_slot,
                    COUNT(s.show_id) AS show_count,
                    ROUND(AVG(CAST(s.booked_seats AS FLOAT) / s.total_seats * 100.0), 2) AS occupancy_pct,
                    ROUND(AVG(s.customer_rating), 2) AS avg_rating
                FROM shows s
                JOIN cinemas c ON s.cinema_id = c.cinema_id
                {where_sql}
                GROUP BY s.show_slot
                ORDER BY occupancy_pct DESC
                """,
                params,
            ).fetchall()
        ]

        cinema_breakdown = [
            dict(r)
            for r in conn.execute(
                f"""
                SELECT
                    c.cinema_name,
                    c.city,
                    COUNT(s.show_id) AS show_count,
                    ROUND(AVG(CAST(s.booked_seats AS FLOAT) / s.total_seats * 100.0), 2) AS occupancy_pct,
                    ROUND(AVG(s.ad_placement_verified) * 100.0, 2) AS ad_compliance_pct
                FROM shows s
                JOIN cinemas c ON s.cinema_id = c.cinema_id
                {where_sql}
                GROUP BY c.cinema_id
                ORDER BY occupancy_pct DESC
                """,
                params,
            ).fetchall()
        ]

        staff_performance = [
            dict(r)
            for r in conn.execute(
                """
                SELECT
                    st.staff_name,
                    st.role,
                    st.shift_type,
                    c.cinema_name,
                    st.attendance_rate,
                    st.audit_score,
                    COUNT(sh.show_id) AS shows_managed,
                    ROUND(COALESCE(AVG(sh.av_quality_score), st.audit_score), 2) AS avg_show_quality
                FROM staff st
                JOIN cinemas c ON st.cinema_id = c.cinema_id
                LEFT JOIN shows sh ON st.staff_id = sh.staff_id
                GROUP BY st.staff_id
                ORDER BY st.audit_score DESC, st.attendance_rate DESC
                """
            ).fetchall()
        ]

        recent_shows = [
            dict(r)
            for r in conn.execute(
                f"""
                SELECT
                    s.show_id,
                    s.show_date,
                    c.cinema_name,
                    s.screen_number,
                    s.movie_title,
                    s.show_slot,
                    s.booked_seats,
                    s.total_seats,
                    ROUND(CAST(s.booked_seats AS FLOAT) / s.total_seats * 100.0, 1) AS occupancy_pct,
                    s.ad_placement_verified,
                    s.av_quality_score,
                    s.customer_rating
                FROM shows s
                JOIN cinemas c ON s.cinema_id = c.cinema_id
                {where_sql}
                ORDER BY s.show_date DESC, s.show_id DESC
                LIMIT 25
                """,
                params,
            ).fetchall()
        ]

        cinemas = [r["cinema_name"] for r in conn.execute("SELECT cinema_name FROM cinemas ORDER BY cinema_name").fetchall()]

    return {
        "kpis": dict(kpis) if kpis else {},
        "slot_breakdown": slot_breakdown,
        "cinema_breakdown": cinema_breakdown,
        "staff_performance": staff_performance,
        "recent_shows": recent_shows,
        "cinemas": cinemas,
    }
