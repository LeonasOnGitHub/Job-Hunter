import logging

from openai import OpenAI

from job_hunter.config import (
    get_openai_api_key,
    get_telegram_config,
    load_profile,
)
from job_hunter.filters.rules import (
    passes_basic_filter,
)
from job_hunter.matching.luna import (
    match_with_luna,
)
from job_hunter.matching.scoring import (
    calculate_local_score,
)
from job_hunter.notifications.telegram import (
    send_telegram_message,
)
from job_hunter.sources.mock import (
    fetch_jobs,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Job Hunter.")

    profile = load_profile()

    # ---------------------------------------------------------
    # 1. Fetch
    # ---------------------------------------------------------

    jobs = fetch_jobs()

    logger.info(
        "Fetched %d jobs.",
        len(jobs),
    )

    # ---------------------------------------------------------
    # 2. Cheap deterministic filtering
    # ---------------------------------------------------------

    candidates = []

    for job in jobs:
        passes, reasons = passes_basic_filter(
            job,
            profile,
        )

        if not passes:
            logger.info(
                "Filtered out: %s (%s)",
                job.title,
                "; ".join(reasons),
            )
            continue

        # -----------------------------------------------------
        # 3. Local scoring
        # -----------------------------------------------------

        score, scoring_reasons = (
            calculate_local_score(
                job,
                profile,
            )
        )

        job.local_score = score

        candidates.append(
            (
                job,
                scoring_reasons,
            )
        )

    logger.info(
        "%d jobs remain after local filtering.",
        len(candidates),
    )

    # ---------------------------------------------------------
    # 4. Sort by local score
    # ---------------------------------------------------------

    candidates.sort(
        key=lambda item: item[0].local_score,
        reverse=True,
    )

    matching_config = profile["matching"]

    minimum_llm_score = matching_config.get(
        "minimum_score_for_llm",
        45,
    )

    maximum_llm_jobs = matching_config.get(
        "maximum_llm_jobs_per_run",
        30,
    )

    llm_candidates = [
        item
        for item in candidates
        if item[0].local_score >= minimum_llm_score
    ][:maximum_llm_jobs]

    logger.info(
        "%d jobs selected for LLM evaluation.",
        len(llm_candidates),
    )

    if not llm_candidates:
        logger.info("No jobs require LLM evaluation.")
        return

    # ---------------------------------------------------------
    # 5. Initialize services
    # ---------------------------------------------------------

    client = OpenAI(
        api_key=get_openai_api_key()
    )

    telegram_token, telegram_chat_id = (
        get_telegram_config()
    )

    minimum_notification_score = (
        matching_config.get(
            "minimum_score_for_notification",
            75,
        )
    )

    # ---------------------------------------------------------
    # 6. LLM matching
    # ---------------------------------------------------------

    for job, scoring_reasons in llm_candidates:

        logger.info(
            "Evaluating with Luna: %s (%s)",
            job.title,
            job.company,
        )

        try:
            result = match_with_luna(
                client,
                job,
                profile,
            )
        except Exception:
            logger.exception(
                "LLM evaluation failed for %s.",
                job.id,
            )
            continue

        logger.info(
            "Result: %s = %.0f/100",
            job.title,
            result.score,
        )

        # -----------------------------------------------------
        # 7. Notify
        # -----------------------------------------------------

        if (
            result.recommend
            and result.score
            >= minimum_notification_score
        ):
            send_telegram_message(
                telegram_token,
                telegram_chat_id,
                job,
                result,
            )

            logger.info(
                "Telegram notification sent for %s.",
                job.id,
            )

    logger.info("Job Hunter finished.")