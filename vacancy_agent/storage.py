import json
from pathlib import Path
from models import Vacancy
from datetime import datetime, timezone
# Чтение и запись JSON

def save_vacancies(vacancies, filename="data/vacancies.json"):
    vacancy_dicts = [vacancy.model_dump(mode="json") for vacancy in vacancies]

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(vacancy_dicts, file, ensure_ascii=False, indent=4)


from models import Vacancy
from pathlib import Path
import json


def load_vacancies(filename="data/vacancies.json"):
    path = Path(filename)

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        return []

    vacancy_dicts = json.loads(content)

    vacancies = [
        Vacancy(**vacancy_dict)
        for vacancy_dict in vacancy_dicts
    ]

    return vacancies

def save_history(vacancy_id, changes, filename="data/history.json"):
    if not changes:
        return

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            history = json.load(file)
    else:
        history = []

    history_entry = {
        "vacancy_id": vacancy_id,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "changes": changes
    }

    history.append(history_entry)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4,
            default=str
        )
def save_ranking(ranked_vacancies, filename="data/ranking.json"):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    ranking_data = []

    for item in ranked_vacancies:
        ranking_data.append({
            "vacancy": item["vacancy"].model_dump(mode="json"),
            "score": item["score"],
            "details": item["details"],
            "available_points": item["available_points"],
            "coverage": item["coverage"],
            "analysis": item["analysis"]
        })

    data = {
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "items": ranking_data
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_ranking(filename="data/ranking.json"):
    path = Path(filename)

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("items", [])

    