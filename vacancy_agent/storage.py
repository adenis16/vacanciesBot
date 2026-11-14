import json
from pathlib import Path
from models import Vacancy
# Чтение и запись JSON

def save_vacancies(vacancies, filename="data/vacancies.json"):
    vacancy_dicts = [vacancy.model_dump(mode="json") for vacancy in vacancies]

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(vacancy_dicts, file, ensure_ascii=False, indent=4)


def load_vacancies(filename="data/vacancies.json"):
    path = Path(filename)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        vacancy_dicts = json.load(file)

    return vacancy_dicts
    