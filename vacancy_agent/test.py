from storage import load_vacancies
from agent import analyze_ranked_vacancies
from storage import save_ranking, load_ranking
import json

vacancies = load_vacancies()

# Подставь здесь способ загрузки своего профиля
with open("data/profile.json", "r", encoding="utf-8") as file:
    profile = json.load(file)

results = analyze_ranked_vacancies(vacancies, profile)

save_ranking(results)

saved_results = load_ranking()

print("Количество сохранённых вакансий:", len(saved_results))

for item in saved_results:
    print("\nНазвание:", item["vacancy"]["title"])
    print("Оценка:", item["score"])
    print("Рекомендация:", item["analysis"]["recommendation"])