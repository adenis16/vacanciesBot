from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator



class Vacancy(BaseModel):
    vacancy_id: str
    source_id: str
    url: str
    title: str
    company: str | None = None
    location: str | None = None
    salary_min: int | None = Field(default=None, ge=0) 
    salary_max: int | None = Field(default=None, ge=0)
    currency: str | None = None
    experience: str | None = None
    employment_type: str | None = None
    work_format: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    optional_skills: list[str] = Field(default_factory=list)
    published_at: date | None = None
    collected_at: datetime

    @model_validator(mode="after")
    def check_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError(
                "Максимальная зарплата не может быть меньше минимальной"
            )

        return self