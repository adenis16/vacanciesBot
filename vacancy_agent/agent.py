from openai import OpenAI
from dotenv import load_dotenv
import os

# Поиск вакансий через Yandex AI

load_dotenv()

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

print(response.output_text)