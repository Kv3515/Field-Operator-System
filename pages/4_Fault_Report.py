import streamlit as st
import db, style

style.inject()
style.hero("Fault <span>Report</span>", "File & track drone faults")

operators  = db.get_operators()
drones     = db.get_drones()
cat_labels = list(db.FAULT_CATEGORIES.values())
cat_keys   = list(db.FAULT_CATEGORIES.keys())
sev_labels = list(db.SEVERITY.values())
sev_keys   = list(db.SEVERITY.keys())
rep_labels = list(db.REPAIR_STATUS.values())
rep_keys   = list(db.REPAIR_STATUS.keys())

SEV_COLOR  = {"Minor": "amber", "Moderate": "amber", "Critical": "red"}
REP_COLOR  = {"Pending": "gray", "In Progress": "blue", "Completed": "green"}

# ── File fault ─────────────────────────────────────────────────────────────────
with st.expander("▸  File New Fault Report", expanded=False):
    with st.form("fault_form", clear_on_submit=True):
        drone_code   = st.selectbox("Drone", drones)
        reported_by  = st.selectbox("Reported By (Op Code)", operators)
        cat_label    = st.selectbox("Fault Category", cat_labels)
        sev_label    = st.selectbox("Severity", sev_labels)
        description  = st.text_area("Description", height=100)
        submitted    = st.form_submit_button("Submit Report", use_container_width=True, type="primary")

    if submitted:
        cat = cat_keys[cat_labels.index(cat_label)]
        sev = sev_keys[sev_labels.index(sev_label)]
        db.add_fault_report(drone_code, cat, sev, description, reported_by)
        st.success(f"Fault filed for {drone_code}.")
        st.rerun()

# ── Open faults ────────────────────────────────────────────────────────────────
style.section("Open Faults")
open_faults = db.get_open_faults()

if not open_faults:
    st.success("No open faults — fleet is clean.")
else:
    for f in open_faults:
        sev    = db.SEVERITY.get(f["severity"], "?")
        cat    = db.FAULT_CATEGORIES.get(f["fault_category"], "?")
        status = db.REPAIR_STATUS.get(f["repair_status"], "?")

        sev_chip  = style.chip(sev, SEV_COLOR.get(sev, "gray"))
        stat_chip = style.chip(status, REP_COLOR.get(status, "gray"))

        with st.container():
            st.markdown(
                f'<div class="fo-fault {sev.lower()}">'
                f'  <div style="display:flex;justify-content:space-between;align-items:flex-start">'
                f'    <div>'
                f'      <div style="font-weight:800;font-size:1rem">{f["drone_code"]}'
                f'        <span style="font-weight:500;font-size:0.8rem;color:#777"> · {cat}</span>'
                f'      </div>'
                f'      <div style="margin:6px 0">{sev_chip} {stat_chip}</div>'
                f'      <div style="font-size:0.8rem;color:#555">{f["description"] or "—"}</div>'
                f'      <div style="font-size:0.65rem;color:#aaa;margin-top:5px">'
                f'        {f["reported_at"][:16]} · {f["reported_by"]}'
                f'      </div>'
                f'    </div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([2, 1])
            new_status_label = col1.selectbox(
                "Update status",
                rep_labels,
                index=rep_keys.index(f["repair_status"]),
                key=f"status_{f['id']}",
                label_visibility="collapsed",
            )
            if col2.button("Update", key=f"btn_{f['id']}", use_container_width=True):
                new_status = rep_keys[rep_labels.index(new_status_label)]
                db.update_fault_status(f["id"], new_status)
                st.rerun()
