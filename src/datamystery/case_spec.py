from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Effect:
    source: str
    target: str
    relationship: str


@dataclass(frozen=True)
class ExpectedFinding:
    key: str
    description: str
    minimum_strength: float


@dataclass(frozen=True)
class CaseSpec:
    schema_version: int
    case_id: str
    title: str
    case_type: str
    difficulty: str
    briefing: str
    primary_cause: str
    affected_segment: str
    incident_date: str
    reveal_summary: str
    causal_graph: tuple[Effect, ...]
    expected_findings: tuple[ExpectedFinding, ...]
    red_herrings: tuple[str, ...]
    generation: dict[str, Any]

    def validate(self) -> None:
        if self.schema_version != 1:
            raise ValueError("Unsupported case-spec schema version")
        if self.difficulty not in {"easy", "medium", "hard"}:
            raise ValueError(f"Unsupported difficulty: {self.difficulty}")
        if not self.case_id or not self.primary_cause or not self.expected_findings:
            raise ValueError("Case id, primary cause, and expected findings are required")
        required = {
            "start_date",
            "end_date",
            "order_count",
            "incident_date",
            "campaign_date",
            "affected_category",
        }
        missing = required - self.generation.keys()
        if missing:
            raise ValueError(f"Missing generation parameters: {sorted(missing)}")
        if self.incident_date != self.generation["incident_date"]:
            raise ValueError("Narrative and generation incident dates disagree")
        if self.affected_segment != self.generation["affected_category"]:
            raise ValueError("Narrative and generation affected segments disagree")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
