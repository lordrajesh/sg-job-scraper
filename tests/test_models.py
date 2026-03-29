"""Tests for the JobListing Pydantic model."""

from datetime import date, datetime
import pytest
from pydantic import ValidationError
from models.job_listing import JobListing


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_job(**overrides) -> JobListing:
    """Create a JobListing with sensible defaults; override any field."""
    defaults = {
        "title": "Data Analyst",
        "company": "Binance",
        "location": "Hong Kong",
        "salary": "HK$30,000 - HK$40,000",
        "description": "Analyze data using SQL and Python.",
        "url": "https://example.com/job/123",
        "posting_date": date(2026, 3, 15),
        "job_type": "full-time",
        "work_mode": "Hybrid",
        "experience_level": "Mid",
        "source": "jobsdb",
    }
    defaults.update(overrides)
    return JobListing(**defaults)


# ---------------------------------------------------------------------------
# Valid creation
# ---------------------------------------------------------------------------

class TestValidCreation:
    def test_all_fields(self):
        job = _make_job()
        assert job.title == "Data Analyst"
        assert job.company == "Binance"
        assert job.location == "Hong Kong"
        assert job.salary == "HK$30,000 - HK$40,000"
        assert job.url == "https://example.com/job/123"
        assert job.posting_date == date(2026, 3, 15)
        assert job.job_type == "full-time"
        assert job.work_mode == "Hybrid"
        assert job.experience_level == "Mid"
        assert job.source == "jobsdb"
        assert isinstance(job.scraped_at, datetime)

    def test_optional_fields_default_to_none(self):
        job = _make_job(salary=None, posting_date=None, job_type=None,
                        work_mode=None, experience_level=None)
        assert job.salary is None
        assert job.posting_date is None
        assert job.job_type is None
        assert job.work_mode is None
        assert job.experience_level is None

    def test_whitespace_stripped_from_title_and_company(self):
        job = _make_job(title="  Senior Analyst  ", company="  HSBC  ")
        assert job.title == "Senior Analyst"
        assert job.company == "HSBC"


# ---------------------------------------------------------------------------
# job_type normalization
# ---------------------------------------------------------------------------

class TestJobTypeNormalization:
    @pytest.mark.parametrize("raw, expected", [
        ("full time", "full-time"),
        ("Full Time", "full-time"),
        ("FULL-TIME", "full-time"),
        ("permanent", "full-time"),
        ("Permanent", "full-time"),
        ("part time", "part-time"),
        ("Part-Time", "part-time"),
        ("contract", "contract"),
        ("temporary", "contract"),
        ("temp", "contract"),
        ("freelance", "freelance"),
        ("internship", "internship"),
    ])
    def test_known_types(self, raw, expected):
        job = _make_job(job_type=raw)
        assert job.job_type == expected

    def test_unknown_type_passthrough(self):
        job = _make_job(job_type="volunteer")
        assert job.job_type == "volunteer"

    def test_none_stays_none(self):
        job = _make_job(job_type=None)
        assert job.job_type is None

    def test_empty_string_becomes_none(self):
        job = _make_job(job_type="")
        assert job.job_type is None


# ---------------------------------------------------------------------------
# work_mode normalization
# ---------------------------------------------------------------------------

class TestWorkModeNormalization:
    @pytest.mark.parametrize("raw, expected", [
        ("remote", "Remote"),
        ("Remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("Hybrid", "Hybrid"),
        ("onsite", "On-site"),
        ("on-site", "On-site"),
        ("on site", "On-site"),
        ("in-office", "On-site"),
        ("office", "On-site"),
    ])
    def test_known_modes(self, raw, expected):
        job = _make_job(work_mode=raw)
        assert job.work_mode == expected

    def test_none_stays_none(self):
        job = _make_job(work_mode=None)
        assert job.work_mode is None


# ---------------------------------------------------------------------------
# experience_level normalization
# ---------------------------------------------------------------------------

class TestExperienceLevelNormalization:
    @pytest.mark.parametrize("raw, expected", [
        ("entry level", "Junior"),
        ("entry", "Junior"),
        ("junior", "Junior"),
        ("jr", "Junior"),
        ("fresh graduate", "Junior"),
        ("graduate", "Junior"),
        ("intern", "Junior"),
        ("trainee", "Junior"),
        ("mid level", "Mid"),
        ("mid-level", "Mid"),
        ("mid", "Mid"),
        ("senior", "Senior"),
        ("sr", "Senior"),
        ("lead", "Senior"),
        ("principal", "Senior"),
        ("manager", "Manager"),
        ("supervisor", "Manager"),
        ("director", "Director+"),
        ("head of", "Director+"),
        ("vp", "Director+"),
        ("vice president", "Director+"),
        ("executive", "Director+"),
        ("c-level", "Director+"),
    ])
    def test_known_levels(self, raw, expected):
        job = _make_job(experience_level=raw)
        assert job.experience_level == expected

    def test_none_stays_none(self):
        job = _make_job(experience_level=None)
        assert job.experience_level is None


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class TestValidationErrors:
    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            _make_job(title="")

    def test_empty_company_raises(self):
        with pytest.raises(ValidationError):
            _make_job(company="")

    def test_empty_url_raises(self):
        with pytest.raises(ValidationError):
            _make_job(url="")

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValidationError):
            _make_job(title="   ")

    def test_whitespace_only_company_raises(self):
        with pytest.raises(ValidationError):
            _make_job(company="   ")


# ---------------------------------------------------------------------------
# to_dict() serialization
# ---------------------------------------------------------------------------

class TestToDict:
    def test_serializes_posting_date(self):
        job = _make_job(posting_date=date(2026, 3, 15))
        d = job.to_dict()
        assert d["posting_date"] == "2026-03-15"

    def test_serializes_none_posting_date(self):
        job = _make_job(posting_date=None)
        d = job.to_dict()
        assert d["posting_date"] is None

    def test_serializes_scraped_at_as_iso(self):
        job = _make_job()
        d = job.to_dict()
        # Should be a valid ISO string
        parsed = datetime.fromisoformat(d["scraped_at"])
        assert isinstance(parsed, datetime)

    def test_returns_dict_type(self):
        job = _make_job()
        d = job.to_dict()
        assert isinstance(d, dict)
        assert d["title"] == "Data Analyst"
        assert d["company"] == "Binance"
        assert d["source"] == "jobsdb"
