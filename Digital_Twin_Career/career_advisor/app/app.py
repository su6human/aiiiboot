import streamlit as st
import json
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Career Advisor Dashboard", page_icon="🚀", layout="wide")

st.title("🎯 Digital Twin Career Engine")
st.markdown("Добро пожаловать в твой личный карьерный дашборд. Здесь собрана аналитика по твоим навыкам и рекомендации для развития.")

st.divider()

# Загружаем данные из JSON
data_path = os.path.join(os.path.dirname(__file__), "..", "career_prediction.json")

try:
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Топ-3 подходящие профессии")
        jobs = data.get("top_3_jobs", [])
        if jobs:
            df = pd.DataFrame(jobs)
            df.columns = ["Профессия", "Совпадение (%)"]
            
            # Интерактивный график с помощью Plotly
            fig = px.bar(df, x="Совпадение (%)", y="Профессия", orientation='h', 
                         title="Уровень совпадения твоих навыков",
                         color="Совпадение (%)", color_continuous_scale="Blues")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("Рекомендуемый путь")
        st.success(data.get("recommended_path", "Путь не найден"))
        
        st.subheader("Что нужно выучить в первую очередь:")
        skills = data.get("priority_skills_to_learn", [])
        for skill in skills:
            st.markdown(f"🔥 **{skill}**")
            
except FileNotFoundError:
    st.error(f"Файл с предсказаниями не найден по пути: {data_path}")
    st.info("Пожалуйста, убедись, что модель `career_model.py` была запущена.")
