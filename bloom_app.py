import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# --- 1. THEME & CLINICAL CONFIG ---
st.set_page_config(page_title="Bloom by The Womb", layout="wide", page_icon="🪷")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Fredoka', sans-serif; background-color: #FFF9FA; }
    .bloom-card { background: white; padding: 20px; border-radius: 25px; border: 2px solid #F0E2E7; box-shadow: 5px 5px 0px #F0E2E7; margin-bottom: 20px; }
    .stButton>button { background: #FFB3C1 !important; color: white !important; border-radius: 30px !important; border: none !important; }
    .critical-alert { background: #FF4D6D; color: white; padding: 20px; border-radius: 20px; font-weight: bold; border: 4px solid #C9184A; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINES ---
if "all_patient_data" not in st.session_state:
    st.session_state.all_patient_data = [] # For the Admin Portal
if "vitals" not in st.session_state:
    st.session_state.vitals = []

# --- 3. LOGIC: POG & BABY SIZE ---
def calculate_pog(lmp):
    diff = (datetime.now().date() - lmp).days
    return diff // 7, diff % 7

def get_fruit_animation(weeks):
    fruits = {4: "🍓", 12: "🍋", 16: "🥑", 24: "🌽", 32: "🥥", 40: "🍉"}
    return next((v for k, v in fruits.items() if weeks <= k), "🌸")

# --- 4. NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "login"

def nav_to(page):
    st.session_state.page = page
    st.rerun()

# --- PAGE: LOGIN ---
if st.session_state.page == "login":
    st.markdown("<h1 style='text-align: center; color: #FF8FA3;'>🪷 Bloom Login</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="bloom-card">', unsafe_allow_html=True)
        name = st.text_input("Full Name")
        role = st.selectbox("Role", ["Patient", "Doctor"])
        if role == "Patient":
            lmp = st.date_input("LMP Date", value=datetime.now() - timedelta(weeks=12))
            risks = st.multiselect("Risk Factors", ["None", "PIH (High BP)", "GDM (Sugar)"])
        else:
            pwd = st.text_input("Doctor Secret Key", type="password")
        
        if st.button("Enter The Womb ✨"):
            st.session_state.user = name
            st.session_state.role = role
            if role == "Patient":
                st.session_state.lmp = lmp
                st.session_state.risks = risks
                nav_to("dashboard")
            elif pwd == "OBGYN2026": # Secret Key
                nav_to("admin")
            else:
                st.error("Invalid Secret Key")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: PATIENT DASHBOARD ---
elif st.session_state.page == "dashboard":
    w, d = calculate_pog(st.session_state.lmp)
    st.sidebar.title(f"Hi, {st.session_state.user}!")
    if st.sidebar.button("🏠 Home"): nav_to("dashboard")
    if st.sidebar.button("🩺 Medical Hub"): nav_to("medical")
    if st.sidebar.button("🤝 Village"): nav_to("village")
    if st.sidebar.button("Logout"): st.session_state.page = "login"; st.rerun()

    st.markdown(f"""
        <div style='text-align: center;'>
            <div style='font-size: 80px;'>{get_fruit_animation(w)}</div>
            <h2>Week {w}, Day {d}</h2>
            <p>Your baby is as big as a <b>{get_fruit_animation(w)}</b>!</p>
        </div>
    """, unsafe_allow_html=True)

    # CHECKLIST
    st.subheader("Personalized Bloom-List 📝")
    tasks = ["Prenatal Vitamin", "Hydration (3L)", "20m Walk", "Talk to Baby", "BP Check", "Sugar Check", "Magnesium", "Pelvic Floor Ex", "Rest period", "Fruit intake"]
    cols = st.columns(2)
    for i, t in enumerate(tasks):
        cols[i % 2].checkbox(t, key=f"task_{i}")

# --- PAGE: MEDICAL HUB (7-POINT GDM & BI-DAILY BP) ---
elif st.session_state.page == "medical":
    st.header("🩺 Your Medical Records")
    
    # GDM 7-POINT LOGIC
    if "GDM (Sugar)" in st.session_state.risks:
        st.markdown('<div class="bloom-card">', unsafe_allow_html=True)
        st.subheader("7-Point GDM Charting")
        
        c1, c2 = st.columns(2)
        slot = c1.selectbox("Reading for:", ["Fasting", "Post-Breakfast (2h)", "Post-Lunch (2h)", "Post-Dinner (2h)", "2 AM"])
        val = c2.number_input("Sugar (mg/dL)", 40, 400, 90)
        if st.button("Save Sugar Log"):
            # Alert Logic
            threshold = 95 if "Fasting" in slot or "2 AM" in slot else 140
            if val > threshold:
                st.warning(f"🚨 Elevated! Follow diet and recheck. Limit is {threshold}.")
            else:
                st.success("Perfect reading!")
            st.session_state.vitals.append({"Type": "Sugar", "Slot": slot, "Value": val, "Date": datetime.now()})
        st.markdown('</div>', unsafe_allow_html=True)

    # PIH BI-DAILY BP
    if "PIH (High BP)" in st.session_state.risks:
        st.markdown('<div class="bloom-card">', unsafe_allow_html=True)
        st.subheader("Bi-Daily Blood Pressure")
        
        c1, c2 = st.columns(2)
        sys = c1.number_input("Systolic (Upper)", 80, 200, 120)
        dia = c2.number_input("Diastolic (Lower)", 40, 130, 80)
        if st.button("Save BP"):
            if sys >= 140 or dia >= 90:
                st.markdown('<div class="critical-alert">🚨 CRITICAL: High BP detected. Rest for 15 mins. If still high, call Dr. Gaurika immediately.</div>', unsafe_allow_html=True)
            st.session_state.vitals.append({"Type": "BP", "Sys": sys, "Dia": dia, "Date": datetime.now()})
        st.markdown('</div>', unsafe_allow_html=True)

    # FETAL MOVEMENT
    st.markdown('<div class="bloom-card">', unsafe_allow_html=True)
    st.subheader("🦶 Kick Counter")
    
    if st.button("I felt a kick!"):
        st.balloons()
    st.info("Decreased Movement? Drink cold juice, lie on your left side, and count for 1 hour. If <10 kicks, call the Dr.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: DOCTOR ADMIN PORTAL ---
elif st.session_state.page == "admin":
    st.header("👩‍⚕️ Doctor's Clinical Oversight")
    st.write("Current High-Risk Patients Flagged Below:")
    
    # Mock data for demonstration (In reality, this would pull from your database)
    admin_data = pd.DataFrame([
        {"Patient": "Mama A", "Risk": "GDM", "Last Sugar": 156, "Status": "🔴 High"},
        {"Patient": "Mama B", "Risk": "PIH", "Last BP": "145/95", "Status": "🔴 High"},
        {"Patient": "Mama C", "Risk": "None", "Last BP": "110/70", "Status": "🟢 Stable"}
    ])
    
    st.table(admin_data)
    st.button("Back to Login", on_click=lambda: nav_to("login"))
