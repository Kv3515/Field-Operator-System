import streamlit as st
import db, style

style.inject()
style.hero("Commander <span>View</span>", "Fleet & operator overview", badge="Read Only")

fleet = db.get_fleet_summary()
today = db.get_today_sorties()

# ── Top metrics ────────────────────────────────────────────────────────────────
style.metrics([
    ("Sorties Today",  str(today["count"])),
    ("Hours Today",    f"{today['hours']:.1f}"),
    ("Serviceable",    str(fleet["serviceable"])),
    ("Open Faults",    str(fleet["open_faults"])),
    ("Grounded",       str(fleet["grounded"])),
])

# ── Operator hours ─────────────────────────────────────────────────────────────
style.section("Operator Flight Hours")
all_hours = db.get_all_operator_hours()
operators = db.get_operators()

active = sorted(
    [(op, all_hours.get(op, 0.0)) for op in operators if all_hours.get(op, 0.0) > 0],
    key=lambda x: x[1], reverse=True,
)
if not active:
    st.info("No flight hours logged yet.")
else:
    max_hrs = active[0][1]
    for op, hrs in active:
        pct = hrs / max_hrs if max_hrs else 0
        bar_w = max(int(pct * 100), 2)
        style.card(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
            f'  <span style="font-weight:800">{op}</span>'
            f'  <span style="font-size:1rem;font-weight:900;color:{style.BRAND}">{hrs:.1f}<span style="font-size:0.7rem;font-weight:400;color:#888"> hrs</span></span>'
            f'</div>'
            f'<div style="background:{style.BORDER};border-radius:4px;height:6px">'
            f'  <div style="width:{bar_w}%;height:100%;background:{style.BRAND};border-radius:4px"></div>'
            f'</div>'
        )

# ── Fleet breakdown ────────────────────────────────────────────────────────────
style.section("Fleet Breakdown")
all_drones   = db.get_drones()
statuses_map = {s["drone_code"]: s for s in db.get_latest_drone_status()}
last_op_map  = db.get_last_operator_per_drone()
drone_locs   = db.get_drone_locations()

ICONS  = {"Serviceable": "🟢", "Minor Fault": "🟡", "Grounded": "🔴", "Under Repair": "🔧"}
COLORS = {"Serviceable": "green", "Minor Fault": "amber", "Grounded": "red", "Under Repair": "blue"}

th = ("padding:8px 12px;text-align:left;font-size:0.65rem;letter-spacing:2px;"
      "text-transform:uppercase;color:#888;font-weight:700")
rows_html = ""
for drone in all_drones:
    s        = statuses_map.get(drone)
    op       = last_op_map.get(drone, "—")
    location = drone_locs.get(drone, "—") or "—"
    label    = db.SERVICEABILITY.get(s["serviceability"], "Unknown") if s else "No Status"
    icon     = ICONS.get(label, "⚪")
    color    = COLORS.get(label, "gray")
    chip     = style.chip(f"{icon} {label}", color)
    rows_html += (
        f'<tr style="border-bottom:1px solid #F5EBE8">'
        f'  <td style="padding:10px 12px;font-weight:800;font-size:0.9rem">{drone}</td>'
        f'  <td style="padding:10px 12px;font-size:0.85rem;color:#555">{op}</td>'
        f'  <td style="padding:10px 12px;font-size:0.85rem;color:#555">{location}</td>'
        f'  <td style="padding:10px 12px">{chip}</td>'
        f'</tr>'
    )

st.markdown(
    f'<div style="border:1.5px solid #EDD8D8;border-radius:12px;overflow:hidden;background:#fff;'
    f'box-shadow:0 2px 12px rgba(139,38,53,0.07)">'
    f'  <table style="width:100%;border-collapse:collapse">'
    f'    <thead>'
    f'      <tr style="background:#F5EBE8;border-bottom:1.5px solid #EDD8D8">'
    f'        <th style="{th}">Drone</th>'
    f'        <th style="{th}">Last Op</th>'
    f'        <th style="{th}">Location</th>'
    f'        <th style="{th}">Status</th>'
    f'      </tr>'
    f'    </thead>'
    f'    <tbody>{rows_html}</tbody>'
    f'  </table>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Recent sorties ─────────────────────────────────────────────────────────────
style.section("Recent Sorties")
logs = db.get_flight_logs(limit=100)
if not logs:
    st.info("No sorties logged.")
else:
    data = [
        {
            "Date":     log["log_date"],
            "Operator": log["op_code"],
            "Drone":    log["drone_code"],
            "Hrs":      log["duration_hrs"],
            "Type":     db.SORTIE_TYPES.get(log["sortie_type"], "?"),
        }
        for log in logs
    ]
    st.dataframe(data, use_container_width=True, hide_index=True)

# ── Open faults table ──────────────────────────────────────────────────────────
style.section("Open Fault Reports")
faults = db.get_open_faults()
if not faults:
    st.success("No open faults.")
else:
    data = [
        {
            "Drone":       f["drone_code"],
            "Category":    db.FAULT_CATEGORIES.get(f["fault_category"], "?"),
            "Severity":    db.SEVERITY.get(f["severity"], "?"),
            "Status":      db.REPAIR_STATUS.get(f["repair_status"], "?"),
            "Reported":    f["reported_at"][:16],
            "By":          f["reported_by"],
            "Description": f["description"],
        }
        for f in faults
    ]
    st.dataframe(data, use_container_width=True, hide_index=True)
