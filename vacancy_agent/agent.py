from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url=os.getenv("OPENAI_API_BASE_URL"),
    project=os.getenv("OPENAI_API_PROJECT")
)

response = client.responses.create(
    model=f"gpt://{os.getenv('YANDEX_FOLDER_ID')}/{os.getenv('YANDEX_MODEL')}",
    input="Ответь одной фразой: подключение к Yandex AI Studio работает.",
    temperature=0.2,
    max_output_tokens=100
)

print(response.output_text)