from job_hunter.models import Job


def calculate_local_score(
    job: Job,
    profile: dict,
) -> tuple[float, list[str]]:
    """
    Calculate a cheap deterministic relevance score.

    This happens before any LLM call.
    """

    profile_data = profile["profile"]

    score = 0.0
    reasons: list[str] = []

    title = job.title.lower()
    description = job.description.lower()

    # ---------------------------------------------------------
    # Preferred title
    # ---------------------------------------------------------

    preferred_titles = profile_data.get(
        "preferred_titles",
        [],
    )

    title_matches = [
        title_name
        for title_name in preferred_titles
        if title_name.lower() in title
    ]

    if title_matches:
        score += 30
        reasons.append(
            f"Titel passt: {title_matches[0]}"
        )

    # ---------------------------------------------------------
    # Skills
    # ---------------------------------------------------------

    skills = profile_data.get(
        "skills",
        [],
    )

    matched_skills = [
        skill
        for skill in skills
        if skill.lower() in description
    ]

    if matched_skills:
        skill_score = min(
            30,
            len(matched_skills) * 7.5,
        )

        score += skill_score

        reasons.append(
            f"Skills: {', '.join(matched_skills)}"
        )

    # ---------------------------------------------------------
    # Seniority
    # ---------------------------------------------------------

    seniority = profile_data.get(
        "seniority",
        [],
    )

    matched_seniority = [
        level
        for level in seniority
        if level.lower() in title
    ]

    if matched_seniority:
        score += 15

        reasons.append(
            f"Seniorität passt: {matched_seniority[0]}"
        )

    # ---------------------------------------------------------
    # Industry
    # ---------------------------------------------------------

    industries = profile_data.get(
        "industries",
        [],
    )

    matched_industries = [
        industry
        for industry in industries
        if industry.lower() in description
    ]

    if matched_industries:
        score += min(
            10,
            len(matched_industries) * 5,
        )

        reasons.append(
            f"Branche: {', '.join(matched_industries)}"
        )

    # ---------------------------------------------------------
    # Remote
    # ---------------------------------------------------------

    if (
        job.remote
        and "remote" in [
            x.lower()
            for x in profile_data.get("locations", [])
        ]
    ):
        score += 5
        reasons.append("Remote möglich.")

    return min(score, 100), reasons