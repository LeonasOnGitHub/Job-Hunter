import json

from openai import OpenAI

from job_hunter.models import Job, MatchResult


SYSTEM_PROMPT = """
Du bist ein präziser Job-Matching-Klassifikator.

Deine Aufgabe ist ausschließlich zu beurteilen, wie gut eine
Stellenanzeige zu einem Kandidatenprofil passt.

Bewerte insbesondere:

- fachliche Anforderungen
- Seniorität
- relevante Skills
- Branche
- Standort / Remote
- Gehalt
- offensichtliche Ausschlusskriterien

Sei konservativ. Ein Job soll nur dann als Empfehlung gelten,
wenn die tatsächliche Passung gut ist.

Gib ausschließlich ein JSON-Objekt mit diesem Schema zurück:

{
  "score": 0,
  "recommend": false,
  "confidence": 0.0,
  "reasons": [],
  "concerns": []
}

score:
0 bis 100

recommend:
true oder false

confidence:
0 bis 1

reasons:
maximal 3 kurze Gründe

concerns:
maximal 3 kurze Bedenken
""".strip()


def _build_payload(
    job: Job,
    profile: dict,
) -> dict:

    profile_data = profile["profile"]

    return {
        "profile": {
            "locations": profile_data.get(
                "locations",
                [],
            ),
            "seniority": profile_data.get(
                "seniority",
                [],
            ),
            "skills": profile_data.get(
                "skills",
                [],
            ),
            "industries": profile_data.get(
                "industries",
                [],
            ),
            "preferred_titles": profile_data.get(
                "preferred_titles",
                [],
            ),
            "salary_min": profile_data.get(
                "salary_min"
            ),
        },
        "job": {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "remote": job.remote,
            "skills": job.extracted_skills,
            "description": job.description,
        },
    }


def match_with_luna(
    client: OpenAI,
    job: Job,
    profile: dict,
) -> MatchResult:

    payload = _build_payload(
        job,
        profile,
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=SYSTEM_PROMPT,
        input=json.dumps(
            payload,
            ensure_ascii=False,
        ),
    )

    result_text = response.output_text

    try:
        data = json.loads(result_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Luna returned invalid JSON."
        ) from exc

    return MatchResult.from_dict(data)