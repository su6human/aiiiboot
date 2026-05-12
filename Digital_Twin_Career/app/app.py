import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import uuid
from groq import Groq

# --- Page Config ---
st.set_page_config(
    page_title="Digital Twin Career Engine",
    page_icon=chr(0x1F680),
    layout="wide",
)

# --- Theme Toggle Logic ---
if "theme" not in st.session_state: st.session_state.theme = "Dark"

with st.sidebar:
    st.markdown(f"### {chr(0x1F3A8)} Оформление")
    st.session_state.theme = st.radio("Выберите тему:", ["Dark", "Light"], horizontal=True)

# --- Design Tokens ---
if st.session_state.theme == "Dark":
    bg_color, sidebar_bg, text_color, sub_text = "#0d0f14", "#151821", "#ffffff", "#a0a0a0"
    accent_1, accent_2, border_color = "#00ffcc", "#b366ff", "rgba(255, 255, 255, 0.1)"
    msg_user_bg, msg_ai_bg, radar_fill = "rgba(0, 255, 204, 0.05)", "rgba(179, 102, 255, 0.05)", "rgba(0, 255, 204, 0.3)"
    card_bg = "rgba(255, 255, 255, 0.03)"
else:
    bg_color, sidebar_bg, text_color, sub_text = "#f4f7fb", "#ffffff", "#1a1f2e", "#6b7280"
    accent_1, accent_2, border_color = "#2563eb", "#7c3aed", "rgba(0, 0, 0, 0.05)"
    msg_user_bg, msg_ai_bg, radar_fill = "rgba(37, 99, 235, 0.05)", "rgba(124, 58, 237, 0.05)", "rgba(37, 99, 235, 0.3)"
    card_bg = "#ffffff"

# --- Dynamic CSS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid {border_color}; }}
    h1 {{ background: linear-gradient(90deg, {accent_1} 0%, {accent_2} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }}
    .job-card {{ background: {card_bg}; border: 1px solid {border_color}; padding: 20px; border-radius: 16px; margin-bottom: 15px; color: {text_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
    .stButton>button {{ background: linear-gradient(90deg, {accent_1} 0%, {accent_2} 100%); color: white !important; border-radius: 10px; font-weight: 700; border: none; width: 100%; }}
    p, span, label, .stMarkdown, .stText, h2, h3 {{ color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# --- RELATIVE DATA LOADING (Fix for Render) ---
def load_data():
    # Ищем файл относительно текущего скрипта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base_dir, "career_advisor", "career_prediction.json")
    
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")
            return None
    return None

data = load_data()

# --- Sidebar ---
st.sidebar.markdown(f"### {chr(0x1F9D1)}{chr(0x200D)}{chr(0x1F4BB)} Актан Кадыркулов")
st.sidebar.markdown(f"{chr(0x1F393)} **Статус:** Студент IT + Бармен")
st.sidebar.divider()

st.sidebar.markdown("### 🔑 Настройки AI")
groq_api_key = st.sidebar.text_input("Введите Groq API Key:", type="password")
st.session_state.groq_api_key = groq_api_key.strip() if groq_api_key else ""

page = st.sidebar.radio("Навигация:", [
    f"{chr(0x1F3E0)} Home", 
    f"{chr(0x1F4C8)} Career Prediction", 
    f"{chr(0x2696)} Balance Wheel", 
    f"{chr(0x1F4AC)} Live Coach", 
    f"{chr(0x1F525)} Roast My Stack"
])

# --- AI Context ---
user_context = "Студент IT, бармен, UI/UX."
if data: 
    missing = data.get('priority_skills_to_learn', [])
    user_context += f" Актуальные цели: {', '.join(missing)}."

SYSTEM_PROMPT = f"Ты — AI-коуч Актана. Контекст: {user_context}."

# --- PAGES ---
if "Home" in page:
    st.markdown("<h1>Мой Digital Twin</h1>", unsafe_allow_html=True)
    top_title = data["top_3_jobs"][0]["title"] if data else "UI/UX Designer"
    top_match = data["top_3_jobs"][0]["match_percent"] if data else 85
    st.markdown(f"<div class='job-card'><h2 style='color:{accent_1};'>{chr(0x1F3AE)} {top_title}</h2><p>Match: {top_match}%</p></div>", unsafe_allow_html=True)

elif "Prediction" in page:
    st.title(f"{chr(0x1F4C8)} Career Prediction")
    if data and "top_3_jobs" in data:
        for job in data["top_3_jobs"]:
            st.markdown(f"<div class='job-card'><h3 style='color:{accent_1};'>{job['title']}</h3><h2 style='font-size:2.5rem;'>{job['match_percent']}%</h2></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Файл career_prediction.json не найден. Проверьте структуру папок в репозитории.")

elif "Wheel" in page:
    st.title(f"{chr(0x2696)} Balance Wheel")
    categories = ['Figma', 'UI/UX', 'Godot', 'HTML/CSS', 'Illustrator', 'Teamwork', 'Communication']
    fig = go.Figure(data=[go.Scatterpolar(r=[90, 75, 60, 70, 85, 80, 85], theta=categories, fill='toself', line_color=accent_1, fillcolor=radar_fill)])
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], color=sub_text, gridcolor=border_color), angularaxis=dict(color=text_color, gridcolor=border_color), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color))
    st.plotly_chart(fig, use_container_width=True)

elif "Coach" in page:
    st.title(f"{chr(0x1F4AC)} Live Coach")
    if not st.session_state.groq_api_key: st.warning("Введите API Key!")
    else:
        if "chats" not in st.session_state: st.session_state.chats = {"default": {"title": "Чат 1", "messages": []}}
        cur = st.session_state.chats["default"]
        for m in cur["messages"]:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Спроси коуча..."):
            cur["messages"].append({"role": "user", "content": prompt})
            try:
                client = Groq(api_key=st.session_state.groq_api_key)
                resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}] + cur["messages"])
                ai_msg = resp.choices[0].message.content
                cur["messages"].append({"role": "assistant", "content": ai_msg})
                st.rerun()
            except Exception as e: st.error(f"Ошибка: {e}")

elif "Roast" in page:
    st.title(f"{chr(0x1F525)} Roast My Stack")
    if st.button("Roast Me!"):
        st.markdown(f"<div class='job-card'><h3>{chr(0x1F525)} БУМ!</h3><p>Иди учи Godot!</p></div>", unsafe_allow_html=True)
