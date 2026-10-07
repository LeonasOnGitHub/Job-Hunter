import httpx

from job_hunter.models import Job, MatchResult


def _format_message(
    job: Job,
    result: MatchResult,
) -> str:

    lines = [
        "🟢 Neuer passender Job",
        "",
        f"{result.score:.0f}/100 — {job.title}",
        "",
        f"🏢 {job.company}",
        f"📍 {job.location}",
    ]

    if (
        job.salary_min is not None
        or job.salary_max is not None
    ):
        minimum = (
            f"{job.salary_min:,}".replace(",", ".")
            if job.salary_min is not None
            else "?"
        )

        maximum = (
            f"{job.salary_max:,}".replace(",", ".")
            if job.salary_max is not None
            else "?"
        )

        lines.append(
            f"💰 {minimum}–{maximum} €"
        )

    if result.reasons:
        lines.extend(
            [
                "",
                "Warum passend:",
            ]
        )

        for reason in result.reasons:
            lines.append(f"• {reason}")

    if result.concerns:
        lines.extend(
            [
                "",
                "⚠️ Zu beachten:",
            ]
        )

        for concern in result.concerns:
            lines.append(f"• {concern}")

    lines.extend(
        [
            "",
            f"🔗 {job.url}",
        ]
    )

    return "\n".join(lines)


def send_telegram_message(
    token: str,
    chat_id: str,
    job: Job,
    result: MatchResult,
) -> None:

    url = (
        f"https://api.telegram.org/bot"
        f"{token}/sendMessage"
    )

    message = _format_message(
        job,
        result,
    )

    response = httpx.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    response.raise_for_status()