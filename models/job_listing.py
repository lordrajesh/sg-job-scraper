"""Pydantic model for a scraped job listing (Hong Kong market)."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class JobListing(BaseModel):
    model_config = {"validate_assignment": True}

    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: str = Field(default="")
    salary: Optional[str] = None
    description: str = Field(default="")
    url: str = Field(..., min_length=1)
    posting_date: Optional[date] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_level: Optional[str] = None
    source: str = Field(..., min_length=1)
    scraped_at: datetime = Field(default_factory=datetime.now)

    @field_validator("title", "company", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("job_type", mode="before")
    @classmethod
    def normalize_job_type(cls, v):
        if not v:
            return None
        v = v.strip().lower()
        mapping = {
            "full time": "full-time",
            "full-time": "full-time",
            "permanent": "full-time",
            "part time": "part-time",
            "part-time": "part-time",
            "contract": "contract",
            "temporary": "contract",
            "temp": "contract",
            "freelance": "freelance",
            "internship": "internship",
        }
        return mapping.get(v, v)

    @field_validator("work_mode", mode="before")
    @classmethod
    def normalize_work_mode(cls, v):
        if not v:
            return None
        v = v.strip().lower()
        mapping = {
            "remote": "Remote",
            "hybrid": "Hybrid",
            "onsite": "On-site",
            "on-site": "On-site",
            "on site": "On-site",
            "in-office": "On-site",
            "office": "On-site",
        }
        return mapping.get(v, v)

    @field_validator("experience_level", mode="before")
    @classmethod
    def normalize_experience(cls, v):
        if not v:
            return None
        v = v.strip().lower()
        mapping = {
            "entry level": "Junior",
            "entry": "Junior",
            "junior": "Junior",
            "jr": "Junior",
            "fresh graduate": "Junior",
            "graduate": "Junior",
            "intern": "Junior",
            "trainee": "Junior",
            "mid level": "Mid",
            "mid-level": "Mid",
            "mid": "Mid",
            "senior": "Senior",
            "sr": "Senior",
            "lead": "Senior",
            "principal": "Senior",
            "manager": "Manager",
            "supervisor": "Manager",
            "director": "Director+",
            "head of": "Director+",
            "vp": "Director+",
            "vice president": "Director+",
            "executive": "Director+",
            "c-level": "Director+",
        }
        return mapping.get(v, v)

    def to_dict(self) -> dict:
        d = self.model_dump()
        d["posting_date"] = str(d["posting_date"]) if d["posting_date"] else None
        d["scraped_at"] = d["scraped_at"].isoformat()
        return d
