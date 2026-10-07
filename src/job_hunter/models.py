from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    source: str

    published_at: datetime | None = None
    remote: bool | None = None
    salary_min: int | None = None
    salary_max: int | None = None

    # Wird später vom lokalen Scoring berechnet.
    local_score: float = 0.0

    # Zusätzliche normalisierte Informationen.
    extracted_skills: list[str] = field(default_factory=list)

    def searchable_text(self) -> str:
        """Returns the text used by local filters and scoring."""

        return " ".join(
            [
                self.title,
                self.company,
                self.location,
                self.description,
                " ".join(self.extracted_skills),
            ]
        ).lower()


@dataclass
class MatchResult:
    score: float
    recommend: bool
    confidence: float
    reasons: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchResult":
        return cls(
            score=float(data.get("score", 0)),
            recommend=bool(data.get("recommend", False)),
            confidence=float(data.get("confidence", 0)),
            reasons=list(data.get("reasons", [])),
            concerns=list(data.get("concerns", [])),
        )