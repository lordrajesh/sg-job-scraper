"""Tests for deduplication logic in merge.py."""

from datetime import date
import pytest
from models.job_listing import JobListing
from merge import (
    normalize,
    canonical_url,
    similarity,
    is_same_job,
    deduplicate,
    _is_generic_company,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _job(**overrides) -> JobListing:
    """Create a JobListing with sensible defaults; override any field."""
    defaults = {
        "title": "Data Analyst",
        "company": "HSBC",
        "location": "Hong Kong",
        "url": "https://example.com/job/1",
        "source": "jobsdb",
    }
    defaults.update(overrides)
    return JobListing(**defaults)


# ---------------------------------------------------------------------------
# normalize / canonical_url / similarity helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_normalize_lowercases_and_strips(self):
        assert normalize("  Data Analyst  ") == "data analyst"

    def test_normalize_removes_special_chars(self):
        assert normalize("Sr. Analyst (Risk)") == "sr analyst risk"

    def test_normalize_empty(self):
        assert normalize("") == ""
        assert normalize(None) == ""

    def test_canonical_url_strips_query_params(self):
        url = "https://jobsdb.com/job/123?utm_source=google&ref=abc"
        assert canonical_url(url) == "https://jobsdb.com/job/123"

    def test_canonical_url_strips_trailing_slash(self):
        assert canonical_url("https://example.com/job/1/") == "https://example.com/job/1"

    def test_canonical_url_lowercases(self):
        assert canonical_url("HTTPS://Example.COM/Job/1") == "https://example.com/job/1"

    def test_canonical_url_empty(self):
        assert canonical_url("") == ""

    def test_similarity_identical(self):
        assert similarity("Data Analyst", "Data Analyst") == 1.0

    def test_similarity_different(self):
        assert similarity("Data Analyst", "Chef de cuisine") < 0.5

    def test_similarity_empty(self):
        assert similarity("", "something") == 0.0


# ---------------------------------------------------------------------------
# is_same_job
# ---------------------------------------------------------------------------

class TestIsSameJob:
    def test_same_url_is_duplicate(self):
        a = _job(url="https://example.com/job/42", source="linkedin")
        b = _job(url="https://example.com/job/42", source="jobsdb",
                 title="Different Title", company="Different Company")
        assert is_same_job(a, b) is True

    def test_same_url_with_tracking_params(self):
        a = _job(url="https://example.com/job/42?utm_source=google")
        b = _job(url="https://example.com/job/42?ref=newsletter")
        assert is_same_job(a, b) is True

    def test_same_title_company_different_url(self):
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://linkedin.com/job/111")
        b = _job(title="Data Analyst", company="HSBC",
                 url="https://jobsdb.com/job/222")
        assert is_same_job(a, b) is True

    def test_different_title_different_company(self):
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://example.com/1")
        b = _job(title="Web Developer", company="Google",
                 url="https://example.com/2")
        assert is_same_job(a, b) is False

    def test_same_title_different_company_different_location(self):
        """Same title but different company AND different location should not match.
        Note: is_same_job has a 'very strong title match + same location' rule,
        so we must use different locations to isolate the company difference."""
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://example.com/1", location="Hong Kong")
        b = _job(title="Data Analyst", company="Goldman Sachs",
                 url="https://example.com/2", location="Singapore")
        assert is_same_job(a, b) is False

    def test_different_title_same_company(self):
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://example.com/1")
        b = _job(title="Software Engineer", company="HSBC",
                 url="https://example.com/2")
        assert is_same_job(a, b) is False


# ---------------------------------------------------------------------------
# deduplicate — URL dedup
# ---------------------------------------------------------------------------

class TestDeduplicateURL:
    def test_exact_url_dedup(self):
        """Same URL from different sources should merge into 1 result."""
        a = _job(url="https://example.com/job/99", source="linkedin")
        b = _job(url="https://example.com/job/99", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 1

    def test_url_with_different_tracking_params_deduped(self):
        a = _job(url="https://example.com/job/99?utm=linkedin")
        b = _job(url="https://example.com/job/99?utm=jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# deduplicate — title+company dedup
# ---------------------------------------------------------------------------

class TestDeduplicateTitleCompany:
    def test_same_title_company_different_url(self):
        """Same title+company from different sources should merge into 1."""
        a = _job(title="Senior Data Analyst", company="Deloitte",
                 url="https://linkedin.com/job/a1", source="linkedin")
        b = _job(title="Senior Data Analyst", company="Deloitte",
                 url="https://jobsdb.com/job/b2", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 1

    def test_case_insensitive_title_company_dedup(self):
        a = _job(title="data analyst", company="hsbc",
                 url="https://a.com/1", source="linkedin")
        b = _job(title="Data Analyst", company="HSBC",
                 url="https://b.com/2", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# deduplicate — different jobs preserved
# ---------------------------------------------------------------------------

class TestDeduplicatePreservesDifferent:
    def test_different_jobs_not_deduped(self):
        """Two genuinely different jobs should both remain."""
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://example.com/1", source="linkedin")
        b = _job(title="Web Developer", company="Google",
                 url="https://example.com/2", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 2

    def test_same_title_different_company_different_location_preserved(self):
        """Same title but different company + different location should be kept separate.
        Note: identical titles at the same location trigger the 'strong title + same
        location' fuzzy rule, so we use different locations to test company isolation."""
        a = _job(title="Data Analyst", company="HSBC",
                 url="https://example.com/1", location="Hong Kong")
        b = _job(title="Data Analyst", company="Goldman Sachs",
                 url="https://example.com/2", location="Singapore")
        result = deduplicate([a, b])
        assert len(result) == 2

    def test_empty_list(self):
        assert deduplicate([]) == []


# ---------------------------------------------------------------------------
# Generic / Confidential company handling
# ---------------------------------------------------------------------------

class TestGenericCompanyHandling:
    def test_confidential_is_generic(self):
        assert _is_generic_company("Confidential") is True
        assert _is_generic_company("confidential") is True

    def test_unknown_is_generic(self):
        assert _is_generic_company("Unknown") is True

    def test_empty_is_generic(self):
        assert _is_generic_company("") is True

    def test_real_company_not_generic(self):
        assert _is_generic_company("HSBC") is False

    def test_confidential_jobs_not_deduped_by_title(self):
        """Two 'Confidential' company jobs with same title should NOT be deduped
        (they could be completely different jobs)."""
        a = _job(title="Data Analyst", company="Confidential",
                 url="https://a.com/1", source="linkedin")
        b = _job(title="Data Analyst", company="Confidential",
                 url="https://b.com/2", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 2

    def test_confidential_jobs_still_deduped_by_url(self):
        """Even for Confidential company, same URL should still dedup."""
        a = _job(title="Data Analyst", company="Confidential",
                 url="https://example.com/same", source="linkedin")
        b = _job(title="Data Analyst", company="Confidential",
                 url="https://example.com/same", source="jobsdb")
        result = deduplicate([a, b])
        assert len(result) == 1
