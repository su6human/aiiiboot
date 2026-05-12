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
    div[data-testid="stChatMessage"] {{ border-radius: 15px !important; margin-bottom: 10px !important; border: 1px solid {border_color} !important; }}
    div[data-testid="stChatMessage"]:has(svg[aria-label="user"]) {{ border-right: 4px solid {accent_1} !important; background: {msg_user_bg} !important; }}
    div[data-testid="stChatMessage"]:has(svg[aria-label="assistant"]) {{ border-left: 4px solid {accent_2} !important; background: {msg_ai_bg} !important; }}
    p, span, label, .stMarkdown, .stText, h2, h3 {{ color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
def load_data():
    p = r"C:\Users\aktan\.gemini\antigravity\scratch\Digital_Twin_Career\career_advisor\career_prediction.json"
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None
data = load_data()

# --- Sidebar ---
st.sidebar.markdown(f"### {chr(0x1F9D1)}{chr(0x200D)}{chr(0x1F4BB)} Актан Кадыркулов")
st.sidebar.markdown(f"{chr(0x1F393)} **Статус:** Студент IT + Бармен")
st.sidebar.divider()

# --- API Key Input (Manual) ---
st.sidebar.markdown("### 🔑 Настройки AI")
groq_api_key = st.sidebar.text_input("Введите Groq API Key:", type="password", help="Вставьте свой ключ gsk_... чтобы активировать чат.")
st.session_state.groq_api_key = groq_api_key.strip() if groq_api_key else ""

page = st.sidebar.radio("Навигация:", [
    f"{chr(0x1F3E0)} Home", 
    f"{chr(0x1F4C8)} Career Prediction", 
    f"{chr(0x2696)} Balance Wheel", 
    f"{chr(0x1F4AC)} Live Coach", 
    f"{chr(0x1F525)} Roast My Stack"
])

# --- AI Context ---
user_context = "Студент IT, бармен, UI/UX. Используй данные Актана для мотивации и советов."
if data: 
    missing = data.get('priority_skills_to_learn', [])
    user_context += f" Актуальные цели по обучению: {', '.join(missing)}."

SYSTEM_PROMPT = f"Ты — Digital Twin Career Engine Актана. Контекст: {user_context}. Отвечай как профессиональный AI-коуч."

# --- PAGES ---
if "Home" in page:
    st.markdown("<h1>Мой Digital Twin Career Engine</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{sub_text};'>📍 Актан Кадыркулов • Бишкек</p>", unsafe_allow_html=True)
    top_title = data["top_3_jobs"][0]["title"] if data else "UI/UX Designer"
    top_match = data["top_3_jobs"][0]["match_percent"] if data else 85
    st.markdown(f"<div class='job-card'><h2 style='color:{accent_1};'>{chr(0x1F3AE)} {top_title}</h2><p>Твой идеальный путь на основе твоих навыков дизайна.</p><p style='color:{accent_2}; font-weight:bold;'>{chr(0x26A1)} Совпадение: {top_match}%</p></div>", unsafe_allow_html=True)

elif "Prediction" in page:
    st.title(f"{chr(0x1F4C8)} Career Prediction")
    if data and "top_3_jobs" in data:
        for job in data["top_3_jobs"]:
            st.markdown(f"<div class='job-card'><h3 style='color:{accent_1};'>{job['title']}</h3><h2 style='font-size:2.5rem; margin:10px 0;'>{job['match_percent']}%</h2><p style='color:{sub_text};'>Missing: {', '.join(data.get('priority_skills_to_learn', []))}</p></div>", unsafe_allow_html=True)

elif "Wheel" in page:
    st.title(f"{chr(0x2696)} Balance Wheel")
    categories = ['Figma', 'UI/UX', 'Godot', 'HTML/CSS', 'Illustrator', 'Teamwork', 'Communication']
    fig = go.Figure(data=[go.Scatterpolar(r=[90, 75, 60, 70, 85, 80, 85], theta=categories, fill='toself', line_color=accent_1, fillcolor=radar_fill)])
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], color=sub_text, gridcolor=border_color), angularaxis=dict(color=text_color, gridcolor=border_color), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_color))
    st.plotly_chart(fig, use_container_width=True)

elif "Coach" in page:
    st.title(f"{chr(0x1F4AC)} Live Coach")
    if not st.session_state.groq_api_key:
        st.warning("⚠️ Пожалуйста, введите свой Groq API Key в боковой панели слева, чтобы начать общение.")
    
    if "chats" not in st.session_state: st.session_state.chats = {}
    if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = "default"
    if "default" not in st.session_state.chats: st.session_state.chats["default"] = {"title": "Чат 1", "messages": []}

    with st.sidebar:
        st.divider()
        st.markdown(f"### {chr(0x1F4AC)} Мои чаты")
        if st.button(f"{chr(0x2795)} Новый чат", use_container_width=True):
            nid = str(uuid.uuid4())[:8]; st.session_state.chats[nid] = {"title": "Новый чат", "messages": []}
            st.session_state.current_chat_id = nid; st.rerun()
        for cid in list(st.session_state.chats.keys()):
            if st.sidebar.button(f"{chr(0x1F4AC)} {st.session_state.chats[cid]['title']}", key=cid, use_container_width=True):
                st.session_state.current_chat_id = cid; st.rerun()

    cur = st.session_state.chats[st.session_state.current_chat_id]
    for m in cur["messages"]:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Напиши своему коучу...", disabled=not st.session_state.groq_api_key):
        if cur["title"] == "Новый чат": cur["title"] = prompt[:20] + "..."
        cur["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        try:
            client = Groq(api_key=st.session_state.groq_api_key)
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}] + cur["messages"], stream=True)
            with st.chat_message("assistant"):
                placeholder = st.empty(); full_resp = ""
                for chunk in resp:
                    if chunk.choices[0].delta.content:
                        full_resp += chunk.choices[0].delta.content; placeholder.markdown(full_resp + "▌")
                placeholder.markdown(full_resp)
            cur["messages"].append({"role": "assistant", "content": full_resp}); st.rerun()
        except Exception as e: st.error(f"Ошибка Groq: {e}")

elif "Roast" in page:
    st.title(f"{chr(0x1F525)} Roast My Stack")
    if st.button(f"{chr(0x1F6A8)} Roast Me!", use_container_width=True):
        st.markdown(f"<div style='background:{'#2a1118' if st.session_state.theme == 'Dark' else '#fee2e2'}; padding:25px; border-radius:16px; border:2px solid #ff0055; color:{'#ffcccc' if st.session_state.theme == 'Dark' else '#991b1b'};'><h3>{chr(0x1F525)} БУМ! {chr(0x1F525)}</h3><p style='font-size:1.2rem;'>Актан, хватит рисовать иконки! Иди учи Godot!</p></div>", unsafe_allow_html=True)
