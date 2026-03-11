import streamlit as st
from datetime import date
import db, style

style.inject()
style.hero("Log <span>Sortie</span>", "Record a flight sortie")

operators    = db.get_operators()
drones       = db.get_drones()
sortie_labels = list(db.SORTIE_TYPES.values())
sortie_keys   = list(db.SORTIE_TYPES.keys())

with st.form("log_sortie_form", clear_on_submit=True):
    op_code      = st.selectbox("Operator", operators)
    drone_code   = st.selectbox("Drone", drones)
    log_date     = st.date_input("Date", value=date.today())
    duration_hrs = st.number_input("Duration (hrs)", min_value=0.1, max_value=24.0,
                                   value=1.0, step=0.1, format="%.1f")
    sortie_label = st.selectbox("Sortie Type", sortie_labels)
    notes        = st.text_area("Notes (optional)", height=80)
    submitted    = st.form_submit_button("Submit Sortie", use_container_width=True, type="primary")

if submitted:
    sortie_type = sortie_keys[sortie_labels.index(sortie_label)]
    db.add_flight_log(op_code, drone_code, duration_hrs, sortie_type, log_date, notes)
    st.success(f"Sortie logged — {op_code} · {drone_code} · {duration_hrs:.1f} hrs")

# ── Recent logs ────────────────────────────────────────────────────────────────
style.section("Recent Sorties")
logs = db.get_flight_logs(limit=50)
if not logs:
    st.info("No sorties logged yet.")
else:
    for log in logs:
        stype     = db.SORTIE_TYPES.get(log["sortie_type"], "?")
        type_chip = style.chip(stype, "blue")
        notes_html = (
            f'<div style="font-size:0.75rem;color:#777;margin-top:5px">{log["notes"]}</div>'
            if log["notes"] else ""
        )
        style.card(
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
            f'  <div>'
            f'    <div class="fo-card-label">{log["log_date"]}</div>'
            f'    <div style="font-weight:800;font-size:1rem;margin:2px 0">'
            f'      {log["op_code"]} &nbsp;·&nbsp; {log["drone_code"]}'
            f'    </div>'
            f'    {notes_html}'
            f'  </div>'
            f'  <div style="text-align:right">'
            f'    <div class="fo-card-value" style="font-size:1.2rem">{log["duration_hrs"]:.1f}<span style="font-size:0.7rem;font-weight:500;color:#888"> hrs</span></div>'
            f'    <div style="margin-top:4px">{type_chip}</div>'
            f'  </div>'
            f'</div>'
        )
