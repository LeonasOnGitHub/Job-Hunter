from job_hunter.models import Job


def fetch_jobs() -> list[Job]:
    """
    Return example jobs.

    This module will later be replaced/extended with real job sources.
    """

    return [
        Job(
            id="mock-001",
            title="Senior Product Manager",
            company="Example SaaS GmbH",
            location="Berlin / Hybrid",
            url="https://example.com/jobs/001",
            source="mock",
            salary_min=80000,
            salary_max=95000,
            remote=True,
            description=(
                "We are looking for a Senior Product Manager to lead "
                "our B2B SaaS product. You will work closely with "
                "engineering, design and customers. Experience with "
                "product management, SaaS and SQL is required."
            ),
        ),
        Job(
            id="mock-002",
            title="Junior Sales Manager",
            company="Example Sales AG",
            location="Berlin",
            url="https://example.com/jobs/002",
            source="mock",
            salary_min=45000,
            salary_max=55000,
            remote=False,
            description=(
                "Join our sales team and develop new customer accounts. "
                "Previous sales experience is helpful."
            ),
        ),
        Job(
            id="mock-003",
            title="Product Lead",
            company="Tech Platform GmbH",
            location="Remote",
            url="https://example.com/jobs/003",
            source="mock",
            salary_min=75000,
            salary_max=100000,
            remote=True,
            description=(
                "Lead product strategy for our growing technology "
                "platform. We are looking for a strong product leader "
                "with experience in SaaS environments, SQL and "
                "cross-functional product teams."
            ),
        ),
        Job(
            id="mock-004",
            title="Software Engineer Python",
            company="Data Systems GmbH",
            location="Munich",
            url="https://example.com/jobs/004",
            source="mock",
            salary_min=75000,
            salary_max=90000,
            remote=True,
            description=(
                "Develop backend services using Python and PostgreSQL. "
                "Strong software engineering experience required."
            ),
        ),
        Job(
            id="mock-005",
            title="Product Owner SaaS",
            company="Digital Solutions GmbH",
            location="Berlin",
            url="https://example.com/jobs/005",
            source="mock",
            salary_min=70000,
            salary_max=85000,
            remote=False,
            description=(
                "As Product Owner you will manage the roadmap of our "
                "B2B SaaS product and collaborate with engineering, "
                "design and business stakeholders."
            ),
        ),
    ]