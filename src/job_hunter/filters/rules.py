from job_hunter.models import Job


def _contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()

    return any(
        term.lower() in text
        for term in terms
    )


def passes_basic_filter(
    job: Job,
    profile: dict,
) -> tuple[bool, list[str]]:
    """
    Apply cheap deterministic filters.

    Returns:
        (passes, reasons)
    """

    reasons: list[str] = []

    profile_data = profile["profile"]

    text = job.searchable_text()

    # ---------------------------------------------------------
    # Excluded terms
    # ---------------------------------------------------------

    excluded_terms = profile_data.get(
        "excluded_terms",
        [],
    )

    matched_exclusions = [
        term
        for term in excluded_terms
        if term.lower() in text
    ]

    if matched_exclusions:
        return (
            False,
            [
                f"Ausschlussbegriff: {term}"
                for term in matched_exclusions
            ],
        )

    # ---------------------------------------------------------
    # Location
    # ---------------------------------------------------------

    locations = profile_data.get(
        "locations",
        [],
    )

    if locations:
        location_match = _contains_any(
            job.location,
            locations,
        )

        # Remote is accepted if Remote is one of the
        # configured locations.
        if (
            not location_match
            and job.remote
            and "remote" in [
                location.lower()
                for location in locations
            ]
        ):
            location_match = True

        if not location_match:
            return (
                False,
                ["Standort passt nicht."],
            )

        reasons.append("Standort passt.")

    # ---------------------------------------------------------
    # Salary
    # ---------------------------------------------------------

    minimum_salary = profile_data.get(
        "salary_min"
    )

    if (
        minimum_salary is not None
        and job.salary_max is not None
        and job.salary_max < minimum_salary
    ):
        return (
            False,
            ["Gehalt liegt unter dem Minimum."],
        )

    if (
        minimum_salary is not None
        and job.salary_max is not None
    ):
        reasons.append("Gehaltsrahmen passt.")

    return True, reasons