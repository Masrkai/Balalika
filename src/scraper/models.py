from typing import Optional
from pydantic import BaseModel

class Salary(BaseModel):
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    currency: Optional[str] = "USD"

class JobRecord(BaseModel):
    country: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    job_title: str
    company_name: str
    location: Optional[str] = None
    salary: Optional[Salary] = None
    job_url: str
    posted_date: Optional[str] = None
    description: Optional[str] = None
