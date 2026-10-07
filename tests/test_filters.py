from job_hunter.filters.rules import passes_basic_filter
from job_hunter.models import Job


PROFILE = {
    "profile": {
        "locations": [
            "Berlin",
            "Remote",
        ],
        "excluded_terms": [
            "Junior",
            "Sales",
            "Vertrieb",
        ],
        "salary_min": 70000,
    }
}


def test_good_job_passes():

    job = Job(
        id="1",
        title="Senior Product Manager",
        company="Test GmbH",
        location="Berlin",
        url="https://example.com",
        source="test",
        description="Senior product manager",
        salary_min=75000,
        salary_max=90000,
    )

    passes, _ = passes_basic_filter(
        job,
        PROFILE,
    )

    assert passes is True


def test_sales_job_is_rejected():

    job = Job(
        id="2",
        title="Sales Manager",
        company="Test GmbH",
        location="Berlin",
        url="https://example.com",
        source="test",
        description="Join our sales team.",
        salary_min=80000,
        salary_max=90000,
    )

    passes, _ = passes_basic_filter(
        job,
        PROFILE,
    )

    assert passes is False


def test_wrong_location_is_rejected():

    job = Job(
        id="3",
        title="Senior Product Manager",
        company="Test GmbH",
        location="Munich",
        url="https://example.com",
        source="test",
        description="Product management",
        salary_min=80000,
        salary_max=90000,
    )

    passes, _ = passes_basic_filter(
        job,
        PROFILE,
    )

    assert passes is False


def test_low_salary_is_rejected():

    job = Job(
        id="4",
        title="Senior Product Manager",
        company="Test GmbH",
        location="Berlin",
        url="https://example.com",
        source="test",
        description="Product management",
        salary_min=40000,
        salary_max=60000,
    )

    passes, _ = passes_basic_filter(
        job,
        PROFILE,
    )

    assert passes is False