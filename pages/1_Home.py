import streamlit as st
import db, style

style.inject()
style.hero("Field <span>Ops</span>", "Sortie & Fleet Management", badge="System Online")

today = db.get_today_sorties()
fleet = db.get_fleet_summary()
open_faults = db.get_open_faults()

# ── Today ──────────────────────────────────────────────────────────────────────
style.section("Today's Activity")
style.metrics([
    ("Sorties", str(today["count"])),
    ("Flight Hrs", f"{today['hours']:.1f}"),
])

# ── Fleet ──────────────────────────────────────────────────────────────────────
style.section("Fleet Status")
style.metrics([
    ("Total", str(fleet["total"])),
    ("Serviceable", str(fleet["serviceable"])),
    ("Minor Fault", str(fleet["faulted"])),
    ("Grounded", str(fleet["grounded"])),
])

# ── Open faults ────────────────────────────────────────────────────────────────
style.section(f"Open Faults ({fleet['open_faults']})")
if not open_faults:
    st.success("No open faults.")
else:
    for f in open_faults:
        sev   = db.SEVERITY.get(f["severity"], "?")
        cat   = db.FAULT_CATEGORIES.get(f["fault_category"], "?")
        status = db.REPAIR_STATUS.get(f["repair_status"], "?")
        sev_color = {"Minor": "amber", "Moderate": "amber", "Critical": "red"}.get(sev, "gray")
        sev_chip = style.chip(sev, sev_color)
        stat_chip = style.chip(status, "blue")
        fault_class = sev.lower()
        style.card(
            f'<div class="fo-card-label">{f["drone_code"]} &nbsp;·&nbsp; {cat}</div>'
            f'<div style="margin:6px 0">{sev_chip} {stat_chip}</div>'
            f'<div style="font-size:0.8rem;color:#555;margin-top:4px">'
            f'{f["description"] or "No description"}'
            f'</div>'
            f'<div style="font-size:0.68rem;color:#aaa;margin-top:6px">'
            f'{f["reported_at"][:16]} · {f["reported_by"]}'
            f'</div>',
            extra_class=fault_class,
        )
