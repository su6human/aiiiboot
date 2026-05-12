# career_model_v2.py - Улучшенная версия для Актана
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

# Твои реальные навыки (обновлённые)
my_skills = [
    "Figma", "Adobe Illustrator", "UI Design", "UX Design", "HTML", "CSS", 
    "Color Theory", "Typography", "Prototyping", "Miro", "Teamwork", 
    "Communication", "Godot", "Animation basics", "Graphic Design"
]

my_skills_text = " ".join(my_skills)

# Более точные профессии с навыками
jobs = {
    "UI/UX Designer": "Figma UI Design UX Design Prototyping Color Theory Typography Miro Communication",
    "Game UI/UX Designer": "Figma Godot Animation UI Design UX Design Prototyping Game Interface",
    "Interactive Designer": "Figma Godot Animation UI Design Prototyping Motion",
    "Frontend Web Designer": "HTML CSS Figma UI Design Responsive Design",
    "Motion Designer": "Animation Figma Adobe Illustrator Motion Graphics",
    "Product Designer": "Figma UX Design Prototyping User Testing Communication",
    "Graphic Designer": "Adobe Illustrator Figma Graphic Design Color Theory Typography",
    "Creative Technologist": "Figma Godot HTML CSS Animation Interactive Design"
}

# Анализ
all_texts = [my_skills_text] + list(jobs.values())
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(all_texts)

similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

job_list = list(jobs.keys())
sorted_jobs = sorted(zip(job_list, similarity_scores), key=lambda x: x[1], reverse=True)

# Вывод
print("🎯 DIGITAL TWIN CAREER MODEL v2")
print("="*60)
print(f"Твои навыки: {', '.join(my_skills)}\n")

print("🏆 ТОП-3 РЕКОМЕНДОВАННЫЕ ПРОФЕССИИ:\n")
for i, (job, score) in enumerate(sorted_jobs[:3], 1):
    match = round(score * 100, 1)
    print(f"{i}. {job} — {match}% совпадение")
    
    # Missing skills
    job_skills = set(jobs[job].lower().split())
    my_set = set(s.lower() for s in my_skills)
    missing = job_skills - my_set
    if missing:
        print(f"   → Чего не хватает: {', '.join(list(missing)[:5])}")
    print()

print("💡 Главная рекомендация:")
print("У тебя отличная база в дизайне + уже есть интерес к Godot.")
print("Самое перспективное направление сейчас — **Game UI/UX Designer** или **Interactive Designer**.")
print("Это позволяет совмещать дизайн и программирование анимаций.")

# Сохраняем результат
result = {
    "top_3_jobs": [{"title": job, "match_percent": round(score*100, 1)} for job, score in sorted_jobs[:3]],
    "recommended_path": "Game UI/UX Designer / Interactive Designer",
    "priority_skills_to_learn": ["Godot advanced", "JavaScript", "Animation principles", "Responsive Design"]
}

with open("career_prediction.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n✅ Результат сохранён в career_prediction.json")