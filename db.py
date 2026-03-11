import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "field.db")

# ── Sortie type labels ────────────────────────────────────────────────────────
SORTIE_TYPES = {1: "Day Ops", 2: "Night Ops", 3: "Training", 4: "Recce", 5: "Other"}

# ── Drone models ──────────────────────────────────────────────────────────────
DRONE_MODELS = [
    "DJI Air 3S",
    "RPAV",
    "DJI Mavic 2 Enterprise",
    "SVL Copter Q5 HA",
    "DJI 4T",
    "DJI Air 2S DJI Mavic 2 Advance",
    "DJI Air 2S",
    "DJI 350 RTK",
    "DJI Awata-2",
    "DJI NEO",
    "DJI Phantom 4",
    "DJI Mavic Mini",
    "Nano Drone - Black Hornet",
]

# ── Serviceability labels ─────────────────────────────────────────────────────
SERVICEABILITY = {
    1: "Serviceable",
    2: "Minor Fault",
    3: "Grounded",
    4: "Under Repair",
}

# ── Fault categories ──────────────────────────────────────────────────────────
FAULT_CATEGORIES = {
    1: "Airframe",
    2: "Propulsion",
    3: "Electronics",
    4: "Battery",
    5: "Payload",
    6: "Software",
}

# ── Severity ──────────────────────────────────────────────────────────────────
SEVERITY = {1: "Minor", 2: "Moderate", 3: "Critical"}

# ── Repair status ─────────────────────────────────────────────────────────────
REPAIR_STATUS = {1: "Pending", 2: "In Progress", 3: "Completed"}


def _conn():
    return sqlite3.connect(DB_PATH)


def init_database():
    with _conn() as con:
        cur = con.cursor()

        # Operators: just codes, no names
        cur.execute("""
            CREATE TABLE IF NOT EXISTS operators (
                op_code   TEXT PRIMARY KEY,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Drones: codes + optional name
        cur.execute("""
            CREATE TABLE IF NOT EXISTS drones (
                drone_code TEXT PRIMARY KEY,
                drone_name TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        # Migrate: add drone_name column if it doesn't exist yet
        cols = [r[1] for r in cur.execute("PRAGMA table_info(drones)").fetchall()]
        if "drone_name" not in cols:
            cur.execute("ALTER TABLE drones ADD COLUMN drone_name TEXT DEFAULT ''")

        # Flight logs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flight_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                op_code       TEXT NOT NULL,
                drone_code    TEXT NOT NULL,
                duration_hrs  REAL NOT NULL,
                sortie_type   INTEGER NOT NULL DEFAULT 1,
                logged_at     TEXT DEFAULT (datetime('now')),
                log_date      TEXT NOT NULL,
                notes         TEXT DEFAULT ''
            )
        """)

        # Drone status snapshots (latest per drone is authoritative)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS drone_status (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                drone_code         TEXT NOT NULL,
                serviceability     INTEGER NOT NULL DEFAULT 1,
                battery_sets_ok    INTEGER NOT NULL DEFAULT 0,
                battery_sets_total INTEGER NOT NULL DEFAULT 0,
                updated_at         TEXT DEFAULT (datetime('now')),
                updated_by         TEXT DEFAULT ''
            )
        """)

        # Fault reports
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fault_reports (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                drone_code     TEXT NOT NULL,
                fault_category INTEGER NOT NULL DEFAULT 1,
                severity       INTEGER NOT NULL DEFAULT 1,
                repair_status  INTEGER NOT NULL DEFAULT 1,
                description    TEXT DEFAULT '',
                reported_at    TEXT DEFAULT (datetime('now')),
                reported_by    TEXT DEFAULT '',
                resolved_at    TEXT
            )
        """)

        con.commit()

        # Seed default operator and drone codes if empty
        existing_ops = cur.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
        if existing_ops == 0:
            for i in range(1, 21):
                cur.execute("INSERT OR IGNORE INTO operators (op_code) VALUES (?)",
                            (f"OP-{i:02d}",))

        existing_drones = cur.execute("SELECT COUNT(*) FROM drones").fetchone()[0]
        if existing_drones == 0:
            for i in range(1, 21):
                cur.execute("INSERT OR IGNORE INTO drones (drone_code) VALUES (?)",
                            (f"D-{i:02d}",))

        con.commit()


# ── Operators ─────────────────────────────────────────────────────────────────
def get_operators():
    with _conn() as con:
        rows = con.execute("SELECT op_code FROM operators ORDER BY op_code").fetchall()
    return [r[0] for r in rows]


# ── Drones ────────────────────────────────────────────────────────────────────
def get_drones():
    with _conn() as con:
        rows = con.execute("SELECT drone_code FROM drones ORDER BY drone_code").fetchall()
    return [r[0] for r in rows]


def get_drone_names():
    """Returns {drone_code: drone_name} for all drones."""
    with _conn() as con:
        rows = con.execute("SELECT drone_code, drone_name FROM drones ORDER BY drone_code").fetchall()
    return {r[0]: r[1] for r in rows}


def set_drone_name(drone_code, drone_name):
    with _conn() as con:
        con.execute("UPDATE drones SET drone_name = ? WHERE drone_code = ?",
                    (drone_name.strip(), drone_code))
        con.commit()


# ── Flight logs ───────────────────────────────────────────────────────────────
def add_flight_log(op_code, drone_code, duration_hrs, sortie_type, log_date, notes=""):
    with _conn() as con:
        con.execute("""
            INSERT INTO flight_logs (op_code, drone_code, duration_hrs, sortie_type, log_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (op_code, drone_code, duration_hrs, sortie_type, str(log_date), notes))
        con.commit()


def get_flight_logs(limit=200):
    with _conn() as con:
        rows = con.execute("""
            SELECT id, op_code, drone_code, duration_hrs, sortie_type, log_date, logged_at, notes
            FROM flight_logs ORDER BY logged_at DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(id=r[0], op_code=r[1], drone_code=r[2], duration_hrs=r[3],
                 sortie_type=r[4], log_date=r[5], logged_at=r[6], notes=r[7])
            for r in rows]


def get_operator_hours(op_code):
    with _conn() as con:
        row = con.execute("""
            SELECT COALESCE(SUM(duration_hrs), 0) FROM flight_logs WHERE op_code = ?
        """, (op_code,)).fetchone()
    return row[0]


def get_all_operator_hours():
    """Returns {op_code: total_hours} for all operators."""
    with _conn() as con:
        rows = con.execute("""
            SELECT op_code, COALESCE(SUM(duration_hrs), 0) as total
            FROM flight_logs GROUP BY op_code
        """).fetchall()
    return {r[0]: r[1] for r in rows}


def get_today_sorties():
    today = str(date.today())
    with _conn() as con:
        rows = con.execute("""
            SELECT COUNT(*), COALESCE(SUM(duration_hrs), 0)
            FROM flight_logs WHERE log_date = ?
        """, (today,)).fetchone()
    return {"count": rows[0], "hours": rows[1]}


# ── Drone status ──────────────────────────────────────────────────────────────
def update_drone_status(drone_code, serviceability, battery_sets_ok,
                        battery_sets_total, updated_by=""):
    with _conn() as con:
        con.execute("""
            INSERT INTO drone_status
                (drone_code, serviceability, battery_sets_ok, battery_sets_total, updated_by)
            VALUES (?, ?, ?, ?, ?)
        """, (drone_code, serviceability, battery_sets_ok, battery_sets_total, updated_by))
        con.commit()


def get_latest_drone_status():
    """Returns the most recent status snapshot for every drone."""
    with _conn() as con:
        rows = con.execute("""
            SELECT ds.drone_code, ds.serviceability, ds.battery_sets_ok,
                   ds.battery_sets_total, ds.updated_at, ds.updated_by
            FROM drone_status ds
            INNER JOIN (
                SELECT drone_code, MAX(id) as max_id FROM drone_status GROUP BY drone_code
            ) latest ON ds.id = latest.max_id
            ORDER BY ds.drone_code
        """).fetchall()
    return [dict(drone_code=r[0], serviceability=r[1], battery_sets_ok=r[2],
                 battery_sets_total=r[3], updated_at=r[4], updated_by=r[5])
            for r in rows]


def get_drone_status(drone_code):
    with _conn() as con:
        row = con.execute("""
            SELECT serviceability, battery_sets_ok, battery_sets_total, updated_at, updated_by
            FROM drone_status WHERE drone_code = ? ORDER BY id DESC LIMIT 1
        """, (drone_code,)).fetchone()
    if row:
        return dict(serviceability=row[0], battery_sets_ok=row[1],
                    battery_sets_total=row[2], updated_at=row[3], updated_by=row[4])
    return dict(serviceability=1, battery_sets_ok=0, battery_sets_total=0,
                updated_at="—", updated_by="—")


# ── Fault reports ─────────────────────────────────────────────────────────────
def add_fault_report(drone_code, fault_category, severity, description, reported_by):
    with _conn() as con:
        con.execute("""
            INSERT INTO fault_reports
                (drone_code, fault_category, severity, repair_status, description, reported_by)
            VALUES (?, ?, ?, 1, ?, ?)
        """, (drone_code, fault_category, severity, description, reported_by))
        con.commit()


def get_open_faults():
    with _conn() as con:
        rows = con.execute("""
            SELECT id, drone_code, fault_category, severity, repair_status,
                   description, reported_at, reported_by
            FROM fault_reports WHERE repair_status != 3
            ORDER BY severity DESC, reported_at DESC
        """).fetchall()
    return [dict(id=r[0], drone_code=r[1], fault_category=r[2], severity=r[3],
                 repair_status=r[4], description=r[5], reported_at=r[6], reported_by=r[7])
            for r in rows]


def get_all_faults(limit=100):
    with _conn() as con:
        rows = con.execute("""
            SELECT id, drone_code, fault_category, severity, repair_status,
                   description, reported_at, reported_by, resolved_at
            FROM fault_reports ORDER BY reported_at DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(id=r[0], drone_code=r[1], fault_category=r[2], severity=r[3],
                 repair_status=r[4], description=r[5], reported_at=r[6],
                 reported_by=r[7], resolved_at=r[8])
            for r in rows]


def update_fault_status(fault_id, repair_status):
    resolved = str(datetime.now()) if repair_status == 3 else None
    with _conn() as con:
        con.execute("""
            UPDATE fault_reports SET repair_status = ?, resolved_at = ? WHERE id = ?
        """, (repair_status, resolved, fault_id))
        con.commit()


# ── Last operator per drone (from most recent flight log) ─────────────────────
def get_last_operator_per_drone():
    """Returns {drone_code: op_code} based on most recent flight log per drone."""
    with _conn() as con:
        rows = con.execute("""
            SELECT fl.drone_code, fl.op_code
            FROM flight_logs fl
            INNER JOIN (
                SELECT drone_code, MAX(id) as max_id FROM flight_logs GROUP BY drone_code
            ) latest ON fl.id = latest.max_id
        """).fetchall()
    return {r[0]: r[1] for r in rows}


# ── Summary counts (for dashboard) ───────────────────────────────────────────
def get_fleet_summary():
    statuses = get_latest_drone_status()
    total = len(get_drones())
    serviceable = sum(1 for s in statuses if s["serviceability"] == 1)
    faulted = sum(1 for s in statuses if s["serviceability"] == 2)
    grounded = sum(1 for s in statuses if s["serviceability"] in (3, 4))
    open_faults = len(get_open_faults())
    return dict(total=total, serviceable=serviceable,
                faulted=faulted, grounded=grounded, open_faults=open_faults)
