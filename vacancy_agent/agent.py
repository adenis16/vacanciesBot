import json

from openai import OpenAI
from dotenv import load_dotenv
from logic import rank_vacancies
import os

# Поиск вакансий через Yandex AI

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_MODEL = os.getenv("YANDEX_MODEL")

client = OpenAI(
    api_key=os.getenv("YANDEX_API_KEY"),
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=os.getenv("YANDEX_FOLDER_ID")
)

response = client.responses.create(
    model=f"gpt://{os.getenv('YANDEX_FOLDER_ID')}/{os.getenv('YANDEX_MODEL')}",
    input="""
Найди до 3 актуальных вакансий Python-разработчика в России.

Для каждой вакансии извлеки:
- source — название сайта с вакансией
- source_id — ID объявления на сайте, если доступен
- url — прямая ссылка на вакансию
- title — название должности
- company — компания
- location — местоположение
- salary_min — минимальная зарплата
- salary_max — максимальная зарплата
- currency — валюта
- experience — требуемый опыт
- employment_type — тип занятости
- work_format — формат работы
- required_skills — обязательные навыки
- optional_skills — желательные навыки
- description — краткое описание обязанностей
- published_at — дата публикации

Правила:
- Не придумывай отсутствующие сведения.
- Если значение неизвестно, используй null.
- Если список навыков неизвестен, используй [].
- Включай только вакансии с реальными ссылками.
- Не добавляй оценку соответствия кандидату.

Верни результат в виде JSON-массива.
Без Markdown и пояснений до или после JSON.
""",
    temperature=0.2,
    max_output_tokens=500,
    tools=[
    {
        "type": "web_search",
        "search_context_size": "medium"
    }
]
)

def parse_ai_json(text):
    text = text.strip()

    # Удаляем Markdown-обёртку
    if text.startswith("```"):
        lines = text.splitlines()

        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)

def analyze_vacancy(vacancy, profile, score_result):
    vacancy_data = vacancy.model_dump(mode="json")

    prompt = f"""
Ты AI-ассистент по анализу вакансий.

Твоя задача — кратко проанализировать вакансию
относительно профиля кандидата.

Детерминированная оценка уже рассчитана Python.
Не изменяй её и не рассчитывай баллы самостоятельно.

Профиль кандидата:
{json.dumps(profile, ensure_ascii=False)}

Данные вакансии:
{json.dumps(vacancy_data, ensure_ascii=False)}

Результат оценки:
{json.dumps(score_result, ensure_ascii=False)}

Проанализируй:
1. Краткое описание вакансии.
2. Основные преимущества для кандидата.
3. Возможные недостатки и риски.
4. Общую рекомендацию.

Учитывай дополнительные параметры:
- optional_skills
- employment_type
- description
- company
- published_at

Не придумывай отсутствующие данные.
Если информации недостаточно, укажи это.
Не повторяй числовую оценку в рекомендации.

Верни только JSON следующей структуры:

{{
    "summary": "Краткое описание вакансии",
    "strengths": [
        "Преимущество 1",
        "Преимущество 2"
    ],
    "risks": [
        "Риск 1"
    ],
    "recommendation": "Краткая рекомендация"
}}
"""

    response = client.responses.create(
        model=f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}",
        input=prompt,
        temperature=0.3,
        max_output_tokens=2000
    )

    result = parse_ai_json(response.output_text)

    return result


def analyze_ranked_vacancies(vacancies, profile, min_coverage=50):
    # Сначала выполняем детерминированное ранжирование
    ranked_vacancies = rank_vacancies(
        vacancies,
        profile,
        min_coverage=min_coverage
    )

    # Затем добавляем AI-анализ к каждой вакансии
    for item in ranked_vacancies:
        score_result = {
            "score": item["score"],
            "details": item["details"],
            "available_points": item["available_points"],
            "coverage": item["coverage"]
        }

        analysis = analyze_vacancy(
            item["vacancy"],
            profile,
            score_result
        )

        item["analysis"] = analysis

    return ranked_vacancies


