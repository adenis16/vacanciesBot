from pydantic import ValidationError
from models import Vacancy
from storage import save_vacancies, load_vacancies
from datetime import datetime, timezone

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

        # Ищем существующую вакансию-дубликат
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
            merged_vacancies[duplicate_index] = update_vacancy(
                old_vacancy,
                new_vacancy
            )

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

# # save_vacancies(valid_vacancies)
vacancies_data = [{
    "vacancy_id": "vacancy_001",
    "source": "rabota.sber.ru",
    "source_id": "4584706",
    "url": "https://rabota.sber.ru/search/python-razrabotchik-4584706/",
    "title": "Python разработчик",
    "company": "ПАО Сбербанк",
    "location": "Москва",
    "salary_min": 100000,
    "salary_max": 150000,
    "currency": "RUB",
    "required_skills": ["Python", "FastAPI"],
    "published_at": "2026-11-10",
    "collected_at": "2026-11-14T12:00:00+03:00"
}]

result = update_vacancies(vacancies_data)
print(result)

# valid_vacancies = []
# invalid_vacancies = []

# for item in vacancies_data:
#     try:
#         vacancy = Vacancy(**item)
#         valid_vacancies.append(vacancy)
#     except ValidationError as error:
#         invalid_vacancies.append({"data": item, "errors": error.errors()})

# save_vacancies(valid_vacancies)
# print(f"Успешно проверено: {len(valid_vacancies)}")
# print(f"Ошибок: {len(invalid_vacancies)}")
# data = load_vacancies()

# print(type(data))
# print(type(data[0]) if data else "Список пуст")


# vacancy_dicts = load_vacancies()

# valid_vacancies = []
# invalid_vacancies = []

# for item in vacancy_dicts:
#     try:
#         vacancy = Vacancy(**item)
#         valid_vacancies.append(vacancy)
#     except ValidationError as error:
#         invalid_vacancies.append({
#             "data": item,
#             "errors": error.errors()
#         })

# print(f"Корректных вакансий: {len(valid_vacancies)}")
# print(f"Некорректных вакансий: {len(invalid_vacancies)}")




# Общие обязательные поля
# base_data = {
#     "source": "hh.ru",
#     "url": "https://hh.ru/vacancy/123",
#     "title": "Python разработчик",
#     "collected_at": datetime.now(timezone.utc),
# }

# # Новая вакансия
# new_vacancy = Vacancy(
#     vacancy_id="new_001",
#     source_id="123",
#     **base_data
# )

# # Сценарий 1: тот же источник и тот же ID
# existing_1 = Vacancy(
#     vacancy_id="old_001",
#     source_id="123",
#     **base_data
# )

# # Сценарий 2: другой источник, но тот же ID
# existing_2 = Vacancy(
#     vacancy_id="old_002",
#     source="rabota.ru",
#     source_id="123",
#     url="https://rabota.ru/vacancy/123",
#     title="Python разработчик",
#     collected_at=datetime.now(timezone.utc)
# )

# # Сценарий 3: тот же источник, другой ID
# existing_3 = Vacancy(
#     vacancy_id="old_003",
#     source="hh.ru",  # Добавили обязательное поле
#     source_id="456",
#     url="https://hh.ru/vacancy/456",
#     title="Python разработчик",
#     collected_at=datetime.now(timezone.utc)
# )

# # Сценарий 4: у новой вакансии нет ID, но URL совпадает
# existing_4 = Vacancy(
#     vacancy_id="old_004",
#     source_id="456",
#     **base_data
# )

# # Проверки
# tests = [
#     ("Одинаковые source и source_id", [existing_1]),
#     ("Разные source, одинаковый source_id", [existing_2]),
#     ("Одинаковый source, разные source_id", [existing_3]),
#     ("Нет ID, одинаковый URL", [existing_4]),
# ]

# new_without_id = Vacancy(
#     vacancy_id="new_002",
#     source_id=None,
#     **base_data
# )

# for name, existing in tests:
#     candidate = new_without_id if name == "Нет ID, одинаковый URL" else new_vacancy
#     result = is_duplicate(candidate, existing)
#     print(f"{name}: {result}")

# merged = merge_vacancies(
#     new_vacancies=[existing_1, existing_1, existing_3],
#     existing_vacancies=[existing_2]
# )

# print(f"Итоговое количество: {len(merged)}")