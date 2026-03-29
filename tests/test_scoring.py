"""Tests for skill matching, TTPS detection, work mode, and seniority."""

import pytest
from generate_data import (
    calc_skill_match,
    detect_ttps_friendly,
    detect_work_mode,
    detect_seniority,
    TTPS_FRIENDLY_COMPANIES,
)


# ---------------------------------------------------------------------------
# calc_skill_match
# ---------------------------------------------------------------------------

class TestCalcSkillMatch:
    def test_data_analyst_title_high_score(self):
        """A 'Data Analyst' title with relevant skills should score high."""
        score = calc_skill_match(
            title="Data Analyst",
            description="Must know SQL, Python, Power BI, Excel, and data analysis.",
            skills_found=["sql", "python", "power bi", "excel"],
        )
        # Title gives 25 pts, plus description skills should push well above 30
        assert score >= 30

    def test_data_analyst_rich_description(self):
        """Data analyst with many matching skills should score very high."""
        score = calc_skill_match(
            title="Senior Data Analyst",
            description=(
                "Requirements: SQL, Python, Power BI, Excel, data analysis, "
                "reporting, dashboard, Snowflake, Google Analytics, KPI tracking."
            ),
            skills_found=["sql", "python", "power bi", "excel", "snowflake"],
        )
        assert score >= 50

    def test_unrelated_title_low_score(self):
        """A completely unrelated job should score near zero."""
        score = calc_skill_match(
            title="Executive Chef",
            description="Cook French cuisine in a 5-star hotel. Lead kitchen team.",
            skills_found=[],
        )
        assert score <= 10

    def test_empty_inputs(self):
        score = calc_skill_match(title="", description="", skills_found=[])
        assert score == 0

    def test_title_only_no_description(self):
        """Title alone should give some score even without description."""
        score = calc_skill_match(
            title="BI Analyst",
            description="",
            skills_found=[],
        )
        assert score >= 15  # "bi analyst" title keyword gives 25

    def test_description_only_no_title_match(self):
        """Skills in description should contribute even with generic title."""
        score = calc_skill_match(
            title="Specialist",
            description="Proficient in SQL, Python, and Excel required.",
            skills_found=["sql", "python", "excel"],
        )
        assert score > 0

    def test_score_capped_at_100(self):
        """Score should never exceed 100 regardless of input."""
        score = calc_skill_match(
            title="Technical SEO Data Analyst Power BI",
            description=(
                "SQL Python Power BI Excel data analysis fraud seo technical seo "
                "reporting dashboard R PHP MySQL javascript wordpress snowflake "
                "power automate google search console google analytics bi kpi html "
                "css aml kyc risk management machine learning pytorch langchain "
                "docker git api django tableau azure aws react node.js dbt bigquery "
                "jira agile sem google ads"
            ),
            skills_found=list(
                "sql python power bi excel snowflake tableau azure".split()
            ),
        )
        assert score <= 100


# ---------------------------------------------------------------------------
# detect_ttps_friendly
# ---------------------------------------------------------------------------

class TestDetectTTPSFriendly:
    def test_known_company_okx(self):
        assert detect_ttps_friendly("", "OKX") is True

    def test_known_company_hsbc(self):
        assert detect_ttps_friendly("", "HSBC Holdings") is True

    def test_known_company_deloitte(self):
        assert detect_ttps_friendly("", "Deloitte Hong Kong") is True

    def test_known_company_google(self):
        assert detect_ttps_friendly("", "Google Asia Pacific") is True

    def test_unknown_company_no_signals(self):
        assert detect_ttps_friendly("Local bakery looking for a cashier.", "Wong's Bakery") is False

    def test_visa_sponsorship_signal(self):
        assert detect_ttps_friendly(
            "We offer visa sponsorship for qualified candidates.",
            "Unknown Corp",
        ) is True

    def test_relocation_support_signal(self):
        assert detect_ttps_friendly(
            "Relocation package available for overseas hires.",
            "Unknown Corp",
        ) is True

    def test_diverse_team_signal(self):
        assert detect_ttps_friendly(
            "Join our diverse team of professionals from 30+ countries.",
            "Unknown Corp",
        ) is True

    def test_empty_inputs(self):
        assert detect_ttps_friendly("", "") is False

    def test_case_insensitive_company_match(self):
        """Company matching should be case-insensitive."""
        assert detect_ttps_friendly("", "DELOITTE") is True
        assert detect_ttps_friendly("", "deloitte") is True
        assert detect_ttps_friendly("", "Deloitte") is True


# ---------------------------------------------------------------------------
# detect_work_mode
# ---------------------------------------------------------------------------

class TestDetectWorkMode:
    def test_fully_remote(self):
        assert detect_work_mode("This is a fully remote position.", "") == "Remote"

    def test_100_percent_remote(self):
        assert detect_work_mode("100% remote work available.", "") == "Remote"

    def test_work_from_home(self):
        assert detect_work_mode("This is a work from home role.", "") == "Remote"

    def test_remote_position(self):
        assert detect_work_mode("remote position in Hong Kong", "") == "Remote"

    def test_hybrid(self):
        assert detect_work_mode("We offer a hybrid working model.", "") == "Hybrid"

    def test_flexible_work(self):
        assert detect_work_mode("flexible work arrangements available.", "") == "Hybrid"

    def test_on_site(self):
        assert detect_work_mode("This is an on-site role at our HK office.", "") == "On-site"

    def test_in_office(self):
        assert detect_work_mode("in-office position, Central district.", "") == "On-site"

    def test_office_based(self):
        assert detect_work_mode("office-based role in Kowloon.", "") == "On-site"

    def test_bare_remote_keyword(self):
        """A bare 'remote' keyword (not part of 'fully remote' etc.) should still match."""
        assert detect_work_mode("remote", "") == "Remote"

    def test_no_signals_returns_empty(self):
        assert detect_work_mode("Great opportunity in finance.", "") == ""

    def test_empty_inputs(self):
        assert detect_work_mode("", "") == ""

    def test_job_type_field_also_checked(self):
        """The job_type parameter should also be checked for keywords."""
        assert detect_work_mode("", "remote") == "Remote"


# ---------------------------------------------------------------------------
# detect_seniority
# ---------------------------------------------------------------------------

class TestDetectSeniority:
    def test_senior_data_analyst(self):
        assert detect_seniority("Senior Data Analyst", "") == "Senior"

    def test_sr_analyst(self):
        assert detect_seniority("Sr. Analyst", "") == "Senior"

    def test_lead_engineer(self):
        assert detect_seniority("Lead Data Engineer", "") == "Senior"

    def test_principal(self):
        assert detect_seniority("Principal Analyst", "") == "Senior"

    def test_junior_developer(self):
        assert detect_seniority("Junior Developer", "") == "Junior"

    def test_intern(self):
        assert detect_seniority("Marketing Intern", "") == "Junior"

    def test_graduate(self):
        assert detect_seniority("Graduate Trainee", "") == "Junior"

    def test_manager(self):
        assert detect_seniority("Analytics Manager", "") == "Manager"

    def test_supervisor(self):
        assert detect_seniority("Team Supervisor", "") == "Manager"

    def test_director(self):
        assert detect_seniority("Director of Analytics", "") == "Director+"

    def test_head_of(self):
        assert detect_seniority("Head of Data", "") == "Director+"

    def test_vp(self):
        assert detect_seniority("VP Engineering", "") == "Director+"

    def test_plain_title_defaults_to_mid(self):
        assert detect_seniority("Data Analyst", "") == "Mid"

    def test_empty_title_defaults_to_mid(self):
        assert detect_seniority("", "") == "Mid"
