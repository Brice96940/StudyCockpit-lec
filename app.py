
import os, sqlite3, pandas as pd, streamlit as st
from datetime import date

APP_TITLE = "📊 StudyCockpit Élec — Public (read‑only)"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "cockpit.db")
SEED_PATH = os.path.join(DATA_DIR, "seed", "cockpit_demo.db")

def ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH) and os.path.exists(SEED_PATH):
        import shutil
        shutil.copyfile(SEED_PATH, DB_PATH)

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def page_dashboard():
    st.subheader("📁 Projets")
    c = conn()
    projects = pd.read_sql_query("SELECT * FROM projects ORDER BY id DESC", c)
    if projects.empty:
        st.info("Aucun projet (seed vide).")
        return
    proj = st.selectbox("Choisir un projet", projects["name"].tolist())
    pid = int(projects[projects["name"]==proj]["id"].iloc[0])

    circuits = pd.read_sql_query("SELECT * FROM circuits WHERE project_id=?", c, params=(pid,))
    bom = pd.read_sql_query("SELECT * FROM bom_items WHERE project_id=?", c, params=(pid,))
    c.close()

    col = st.columns(3)
    col[0].metric("Circuits", len(circuits))
    col[1].metric("Articles BOM", len(bom))
    total_w = (circuits["qty"]*circuits["power_w"]).fillna(0).sum() if not circuits.empty else 0
    col[2].metric("Puissance totale (W)", f"{int(total_w):,}".replace(","," "))

    with st.expander("🔌 Circuits (lecture seule)", expanded=True):
        st.dataframe(circuits.drop(columns=[c for c in ["id","project_id"] if c in circuits.columns]), use_container_width=True, hide_index=True)
    with st.expander("📦 BOM (lecture seule)", expanded=False):
        st.dataframe(bom.drop(columns=[c for c in ["id","project_id"] if c in bom.columns]), use_container_width=True, hide_index=True)

def three_phase_current_kw(kW, U, pf=0.9, eff=1.0):
    return (kW*1000.0) / (3**0.5 * U * pf * eff)

def single_phase_current_kw(kW, U, pf=0.9, eff=1.0):
    return (kW*1000.0) / (U * pf * eff)

def vdrop_percent(i_current, L, mV_A_m, U):
    return (i_current * mV_A_m * L / 1000.0) / U * 100.0

AMPACITY_TABLE = pd.DataFrame([
    {"csa_mm2": 1.5, "A": 15, "mV_A_m": 29.0},
    {"csa_mm2": 2.5, "A": 21, "mV_A_m": 18.0},
    {"csa_mm2": 4,   "A": 28, "mV_A_m": 11.0},
    {"csa_mm2": 6,   "A": 36, "mV_A_m": 7.3},
    {"csa_mm2": 10,  "A": 50, "mV_A_m": 4.4},
    {"csa_mm2": 16,  "A": 68, "mV_A_m": 2.8},
    {"csa_mm2": 25,  "A": 89, "mV_A_m": 1.75},
    {"csa_mm2": 35,  "A": 110,"mV_A_m": 1.25},
    {"csa_mm2": 50,  "A": 140,"mV_A_m": 0.93},
])

def page_cable_demo():
    st.subheader("🧮 Cable sizing (demo)")
    phases = st.selectbox("Phases", [1,3], index=1)
    kW = st.number_input("Puissance (kW)", 0.0, 2000.0, 5.0, 0.1)
    U = st.number_input("Tension (V)", 12.0, 1000.0, 400.0 if phases==3 else 230.0, 1.0)
    pf = st.number_input("Facteur de puissance (pf)", 0.1, 1.0, 0.9, 0.01)
    eff = st.number_input("Rendement (η)", 0.1, 1.0, 1.0, 0.01)
    L = st.number_input("Longueur (m)", 1.0, 5000.0, 50.0, 1.0)

    I = three_phase_current_kw(kW, U, pf, eff) if phases==3 else single_phase_current_kw(kW, U, pf, eff)
    st.metric("Courant estimé I", f"{I:.1f} A")

    csa_row = AMPACITY_TABLE.loc[AMPACITY_TABLE["A"] >= 1.25*I].head(1)
    if csa_row.empty:
        csa_row = AMPACITY_TABLE.tail(1)
    csa = float(csa_row["csa_mm2"].iloc[0])
    mVAm = float(csa_row["mV_A_m"].iloc[0])
    drop = vdrop_percent(I, L, mVAm, U)
    c1,c2,c3 = st.columns(3)
    c1.metric("Section suggérée", f"{csa} mm²")
    c2.metric("Coeff mV/A/m", f"{mVAm}")
    c3.metric("ΔU % (approx.)", f"{drop:.2f}%")
    with st.expander("Table d'ampacité (démo)"):
        st.dataframe(AMPACITY_TABLE, use_container_width=True, hide_index=True)

    st.caption("Formules: I_mono=P/(U·pf·η), I_tri=P/(√3·U·pf·η), ΔU%≈I·(mV/A/m)·L/U·100")

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
    ensure_db()
    st.title(APP_TITLE)
    st.caption(f"DB: {DB_PATH}")
    tabs = st.tabs(["📊 Dashboard", "🧮 Cable demo"])
    with tabs[0]: page_dashboard()
    with tabs[1]: page_cable_demo()

if __name__ == "__main__":
    main()
