from pydantic import ValidationError
from models import Vacancy
from storage import save_vacancies, load_vacancies, save_history
from datetime import datetime, timezone
import re


# Обработка, проверка и сравнение вакансий

def is_duplicate(new_vacancy, existing_vacancies):
    for vacancy in existing_vacancies:
        if new_vacancy.source_id and vacancy.source_id:
            if new_vacancy.source_id == vacancy.source_id and new_vacancy.source == vacancy.source:
                return True 
        else:
            if new_vacancy.url == vacancy.url:
                return True
    return False

def merge_vacancies(new_vacancies, existing_vacancies):
    merged_vacancies = existing_vacancies.copy()

    for new_vacancy in new_vacancies:
        duplicate_index = None

        # Ищем дубликат
        for index, old_vacancy in enumerate(merged_vacancies):
            if is_duplicate(new_vacancy, [old_vacancy]):
                duplicate_index = index
                break

        # Если дубликат не найден — добавляем новую вакансию
        if duplicate_index is None:
            merged_vacancies.append(new_vacancy)

        # Если найден — обновляем существующую
        else:
            old_vacancy = merged_vacancies[duplicate_index]

            # Определяем изменения
            changes = get_vacancy_changes(old_vacancy, new_vacancy)

            # Сохраняем изменения в истории
            if changes:
                save_history(old_vacancy.vacancy_id, changes)

            # Обновляем вакансию
            updated_vacancy = update_vacancy(
                old_vacancy,
                new_vacancy
            )

            merged_vacancies[duplicate_index] = updated_vacancy

    return merged_vacancies

def update_vacancy(old_vacancy, new_vacancy):
    old_data = old_vacancy.model_dump()
    new_data = new_vacancy.model_dump()

    protected_fields = {
        "vacancy_id",
        "source",
        "source_id",
        "collected_at"
    }

    for field, value in new_data.items():
        if field in protected_fields:
            continue

        if value is not None:
            old_data[field] = value

    return Vacancy(**old_data)
    

def update_vacancies(new_vacancies):
    valid_vacancies = []
    invalid_vacancies = []

    for item in new_vacancies:
        try:
            vacancy = Vacancy(**item)
            valid_vacancies.append(vacancy)
        except ValidationError as error:
            invalid_vacancies.append({"data": item, "errors": error.errors()})

    existing_vacancies_dict = load_vacancies()
    existing_vacancies = [Vacancy(**item) for item in existing_vacancies_dict]
    merged_vacancies = merge_vacancies(valid_vacancies, existing_vacancies)
    save_vacancies(merged_vacancies)
    return {
        "valid": len(valid_vacancies),
        "invalid": len(invalid_vacancies),
        "total": len(merged_vacancies)
    }

def get_vacancy_changes(old_vacancy, new_vacancy): 
    old_data = old_vacancy.model_dump()
    new_data = new_vacancy.model_dump()

    protected_fields = {
        "vacancy_id",
        "source",
        "source_id",
        "collected_at"
    }

    changes = {}

    for field, new_value in new_data.items():
        if field in protected_fields:
            continue

        if new_value is None:
            continue

        old_value = old_data[field]

        if old_value != new_value:
            changes[field] = {
                "old": old_value,
                "new": new_value
            }

    return changes

def parse_experience(value):
    if not value:
        return None

    value = value.lower().strip().replace(",", ".")

    # Диапазон: 3-6 лет, 1–3 года
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)",
        value
    )

    if match:
        return float(match.group(1)), float(match.group(2))

    # От N лет / не менее N лет
    match = re.search(
        r"(?:от|не\s+менее)\s*(\d+(?:\.\d+)?)",
        value
    )

    if match:
        return float(match.group(1)), None

    # До N лет
    match = re.search(
        r"до\s*(\d+(?:\.\d+)?)",
        value
    )

    if match:
        return 0.0, float(match.group(1))

    return None

def compare_experience(candidate_experience, vacancy_experience):
    candidate = parse_experience(candidate_experience)
    vacancy = parse_experience(vacancy_experience)

    if candidate is None or vacancy is None:
        return None

    candidate_min, candidate_max = candidate
    vacancy_min, vacancy_max = vacancy

    # Проверяем полное соответствие диапазонов
    if (
    candidate_min >= vacancy_min
    and (
        vacancy_max is None
        or (
            candidate_max is not None
            and candidate_max <= vacancy_max
        )
    )
    ):
        return 15

    # Проверяем пересечение диапазонов
    candidate_upper = (
        float("inf") if candidate_max is None else candidate_max
    )
    vacancy_upper = (
        float("inf") if vacancy_max is None else vacancy_max
    )

    if max(candidate_min, vacancy_min) <= min(
        candidate_upper, vacancy_upper
    ):
        return 10

    return 0


def calculate_score(vacancy, profile):
    score = 0
    max_score = 0
    details = {}

    # 1. Обязательные навыки
    vacancy_skills = {
        skill.lower() for skill in vacancy.required_skills
    }
    profile_skills = {
        skill.lower() for skill in profile.get("required_skills", [])
    }

    if vacancy_skills and profile_skills:
        matched_skills = vacancy_skills & profile_skills

        points = 40 * len(matched_skills) / len(profile_skills)

        score += points
        max_score += 40

        details["required_skills"] = {
            "score": round(points, 2),
            "max_score": 40,
            "matched": sorted(matched_skills),
            "missing": sorted(profile_skills - vacancy_skills)
        }
    else:
        details["required_skills"] = None

    # 2. Минимальная зарплата
    salary_min = profile.get("salary_min")

    if vacancy.salary_min is not None and salary_min is not None:
        points = 15 if vacancy.salary_min >= salary_min else 0

        score += points
        max_score += 15

        details["salary_min"] = {
            "score": points,
            "max_score": 15
        }
    else:
        details["salary_min"] = None

    # 3. Максимальная зарплата
    salary_max = profile.get("salary_max")

    if vacancy.salary_max is not None and salary_max is not None:
        if vacancy.salary_max >= salary_max:
            points = 15
        elif vacancy.salary_max >= salary_max * 0.9:
            points = 10
        elif vacancy.salary_max >= salary_max * 0.7:
            points = 5
        else:
            points = 0

        score += points
        max_score += 15

        details["salary_max"] = {
            "score": points,
            "max_score": 15
        }
    else:
        details["salary_max"] = None

    # 4. Опыт
    candidate_experience = profile.get("experience")
    vacancy_experience = vacancy.experience

    experience_points = compare_experience(
        candidate_experience,
        vacancy_experience
        )

    if experience_points is not None:
        score += experience_points
        max_score += 15

        details["experience"] = {
            "score": experience_points,
            "max_score": 15
    }
    else:
        details["experience"] = None

    # 5. Местоположение
    if vacancy.work_format != "remote":
        location = profile.get("location")

        if vacancy.location and location:
            points = (
                15
                if vacancy.location.lower() == location.lower()
                else 0
            )

            score += points
            max_score += 15

            details["location"] = {
                "score": points,
                "max_score": 15
            }
        else:
            details["location"] = None
    else:
        details["location"] = None

    if max_score == 0:
        return {
            "score": None,
            "details": details,
            "available_points": 0
        }
    coverage = round(max_score, 2)

    return {
        "score": round(score / max_score * 100, 2),
        "details": details,
        "available_points": max_score,
        "coverage": coverage
}


def rank_vacancies(vacancies, profile, min_coverage=50):
    ranked_vacancies = []

    for vacancy in vacancies:
        result = calculate_score(vacancy, profile)

        ranked_vacancies.append({
            "vacancy": vacancy,
            "score": result["score"],
            "details": result["details"],
            "available_points": result["available_points"],
            "coverage": result["coverage"], 
        })

    ranked_vacancies.sort(
        key=lambda item: (
            item["score"] is None,
            item["coverage"] < min_coverage,
            -(item["score"] or 0),
            -item["coverage"]
        )
    )

    return ranked_vacancies


