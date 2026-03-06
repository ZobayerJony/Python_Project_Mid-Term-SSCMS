from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sscms.config import DATE_FMT


def today_iso() -> str:
    return date.today().strftime(DATE_FMT)


@dataclass
class CaseActivity:
    """
    Timeline entry: follow-up note, status update, phone call, etc.
    """
    timestamp: str  # "YYYY-MM-DD HH:MM"
    action: str     # e.g., "Note", "Status Change", "Phone Call"
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "CaseActivity":
        return CaseActivity(**d)


@dataclass
class SurvivorCase:
    """
    Entity model for a Survivor Support case.
    Includes an activity timeline for advanced tracking.
    """
    case_id: int
    survivor_name: str
    phone: str
    case_type: str
    priority: str
    status: str
    assigned_worker: str
    incident_date: str
    created_at: str
    notes: str = ""
    activities: List[CaseActivity] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.activities is None:
            self.activities = []

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["activities"] = [a.to_dict() for a in self.activities]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SurvivorCase":
        acts = [CaseActivity.from_dict(x) for x in d.get("activities", [])]
        dd = dict(d)
        dd["activities"] = acts
        return SurvivorCase(**dd)

    def add_activity(self, action: str, detail: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.activities.insert(0, CaseActivity(timestamp=ts, action=action, detail=detail.strip()))

    def days_open(self) -> Optional[int]:
        if self.status in ("Resolved", "Closed"):
            return None
        try:
            created = datetime.strptime(self.created_at, DATE_FMT).date()
            return (date.today() - created).days
        except ValueError:
            return None


# minor update for new git commit