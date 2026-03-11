import streamlit as st
import db, style

style.inject()
style.hero("Drone <span>Status</span>", "Fleet serviceability & batteries")

operators  = db.get_operators()
drones     = db.get_drones()
svc_labels = list(db.SERVICEABILITY.values())
svc_keys   = list(db.SERVICEABILITY.keys())

SVC_CHIP = {
    "Serviceable":  ("green",  "🟢"),
    "Minor Fault":  ("amber",  "🟡"),
    "Grounded":     ("red",    "🔴"),
    "Under Repair": ("blue",   "🔧"),
}

# ── Update form ────────────────────────────────────────────────────────────────
with st.expander("▸  Update Drone Status", expanded=False):
    with st.form("drone_status_form", clear_on_submit=True):
        drone_code   = st.selectbox("Drone", drones)
        updated_by   = st.selectbox("Updated By (Op Code)", operators)
        svc_label    = st.selectbox("Serviceability", svc_labels)
        c1, c2       = st.columns(2)
        battery_ok   = c1.number_input("Battery Sets OK",    min_value=0, value=0, step=1)
        battery_total = c2.number_input("Battery Sets Total", min_value=0, value=0, step=1)
        submitted    = st.form_submit_button("Update Status", use_container_width=True, type="primary")

    if submitted:
        svc = svc_keys[svc_labels.index(svc_label)]
        db.update_drone_status(drone_code, svc, battery_ok, battery_total, updated_by)
        st.success(f"{drone_code} updated.")
        st.rerun()

# ── Fleet list ─────────────────────────────────────────────────────────────────
style.section("Fleet Status")
statuses = {s["drone_code"]: s for s in db.get_latest_drone_status()}

for drone in drones:
    s = statuses.get(drone)
    if s:
        label = db.SERVICEABILITY.get(s["serviceability"], "?")
        color, icon = SVC_CHIP.get(label, ("gray", "⚪"))
        chip_html   = style.chip(label, color)
        batt = f"{s['battery_sets_ok']}/{s['battery_sets_total']}" if s["battery_sets_total"] else "—"
        style.card(
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'  <div>'
            f'    <div style="font-size:1rem;font-weight:800">{icon} {drone}</div>'
            f'    <div style="margin-top:5px">{chip_html}</div>'
            f'  </div>'
            f'  <div style="text-align:right">'
            f'    <div class="fo-card-label">Batteries</div>'
            f'    <div style="font-weight:800;font-size:1rem">{batt}</div>'
            f'    <div style="font-size:0.65rem;color:#aaa;margin-top:4px">'
            f'      {s["updated_by"]} · {s["updated_at"][:16]}'
            f'    </div>'
            f'  </div>'
            f'</div>'
        )
    else:
        style.card(
            f'<div style="font-weight:700;color:#bbb">⚪ {drone}</div>'
            f'<div style="font-size:0.72rem;color:#ccc;margin-top:3px">No status recorded</div>',
        )
