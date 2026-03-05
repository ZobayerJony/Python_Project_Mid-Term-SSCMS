from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sscms.config import VALID_CASE_TYPES, VALID_PRIORITIES, VALID_STATUSES
from sscms.models import SurvivorCase, today_iso
from sscms.storage import JsonStore
from sscms.utils import is_valid_date, is_valid_phone, normalize_ws


@dataclass
class CaseManager:
    """
    Business logic layer for SSCMS:
    - CRUD
    - Search
    - Filter/Sort
    - Reports
    - Auto activity logging
    """
    store: JsonStore
    next_id: int = 1
    cases: List[SurvivorCase] = None  # type: ignore

    def __post_init__(self) -> None:
        loaded = self.store.load_cases()
        self.next_id = loaded["next_id"]
        self.cases = loaded["cases"]

    def _persist(self) -> None:
        self.store.save_cases(self.next_id, self.cases)

    # ---------------- Validation ----------------
    def validate(
        self,
        survivor_name: str,
        phone: str,
        case_type: str,
        priority: str,
        status: str,
        assigned_worker: str,
        incident_date: str,
    ) -> Tuple[bool, str]:
        survivor_name = normalize_ws(survivor_name)
        assigned_worker = normalize_ws(assigned_worker)
        phone = phone.strip()
        incident_date = incident_date.strip()

        if not survivor_name:
            return False, "Survivor name is required."
        if not is_valid_phone(phone):
            return False, "Phone invalid. Use digits/spaces/+/- (7–20 chars)."
        if case_type not in VALID_CASE_TYPES:
            return False, "Invalid case type."
        if priority not in VALID_PRIORITIES:
            return False, "Invalid priority."
        if status not in VALID_STATUSES:
            return False, "Invalid status."
        if not assigned_worker:
            return False, "Assigned worker is required."
        if not is_valid_date(incident_date):
            return False, "Incident date must be YYYY-MM-DD."
        return True, ""

    # ---------------- CRUD ----------------
    def add_case(
        self,
        survivor_name: str,
        phone: str,
        case_type: str,
        priority: str,
        status: str,
        assigned_worker: str,
        incident_date: str,
        notes: str = "",
    ) -> Tuple[bool, str, Optional[SurvivorCase]]:
        ok, msg = self.validate(survivor_name, phone, case_type, priority, status, assigned_worker, incident_date)
        if not ok:
            return False, msg, None

        case = SurvivorCase(
            case_id=self.next_id,
            survivor_name=normalize_ws(survivor_name),
            phone=phone.strip(),
            case_type=case_type,
            priority=priority,
            status=status,
            assigned_worker=normalize_ws(assigned_worker),
            incident_date=incident_date.strip(),
            created_at=today_iso(),
            notes=notes.strip(),
        )
        case.add_activity("Created", f"Case created with status '{status}' and priority '{priority}'.")
        if notes.strip():
            case.add_activity("Note", notes.strip())

        self.cases.append(case)
        self.next_id += 1
        self._persist()
        return True, "Case added successfully.", case

    def get_by_id(self, case_id: int) -> Optional[SurvivorCase]:
        for c in self.cases:
            if c.case_id == case_id:
                return c
        return None

    def update_case(
        self,
        case_id: int,
        survivor_name: str,
        phone: str,
        case_type: str,
        priority: str,
        status: str,
        assigned_worker: str,
        incident_date: str,
        notes: str = "",
        add_activity_note: str = "",
    ) -> Tuple[bool, str]:
        case = self.get_by_id(case_id)
        if not case:
            return False, "Case not found."

        ok, msg = self.validate(survivor_name, phone, case_type, priority, status, assigned_worker, incident_date)
        if not ok:
            return False, msg

        # Track changes for activity log
        changes = []
        if case.status != status:
            changes.append(f"Status: {case.status} → {status}")
        if case.priority != priority:
            changes.append(f"Priority: {case.priority} → {priority}")
        if case.assigned_worker != normalize_ws(assigned_worker):
            changes.append(f"Worker: {case.assigned_worker} → {normalize_ws(assigned_worker)}")

        case.survivor_name = normalize_ws(survivor_name)
        case.phone = phone.strip()
        case.case_type = case_type
        case.priority = priority
        case.status = status
        case.assigned_worker = normalize_ws(assigned_worker)
        case.incident_date = incident_date.strip()
        case.notes = notes.strip()

        if changes:
            case.add_activity("Updated", "; ".join(changes))
        if add_activity_note.strip():
            case.add_activity("Follow-up", add_activity_note.strip())

        self._persist()
        return True, "Case updated successfully."

    def delete_case(self, case_id: int) -> Tuple[bool, str]:
        before = len(self.cases)
        self.cases = [c for c in self.cases if c.case_id != case_id]
        if len(self.cases) == before:
            return False, "Case not found."
        self._persist()
        return True, "Case deleted."

    # ---------------- Search / Filter / Sort ----------------
    def search(self, query: str) -> List[SurvivorCase]:
        q = query.strip().lower()
        if not q:
            return list(self.cases)
        out = []
        for c in self.cases:
            hay = (
                f"{c.case_id} {c.survivor_name} {c.phone} "
                f"{c.case_type} {c.priority} {c.status} {c.assigned_worker} {c.notes}"
            ).lower()
            if q in hay:
                out.append(c)
        return out

    def filter_cases(
        self,
        cases: List[SurvivorCase],
        status: str = "All",
        priority: str = "All",
        case_type: str = "All",
        worker: str = "All",
    ) -> List[SurvivorCase]:
        out = cases
        if status != "All":
            out = [c for c in out if c.status == status]
        if priority != "All":
            out = [c for c in out if c.priority == priority]
        if case_type != "All":
            out = [c for c in out if c.case_type == case_type]
        if worker != "All":
            out = [c for c in out if c.assigned_worker == worker]
        return out

    def sort_cases(self, cases: List[SurvivorCase], key: str, descending: bool) -> List[SurvivorCase]:
        def k(c: SurvivorCase):
            if key == "ID":
                return c.case_id
            if key == "Name":
                return c.survivor_name.lower()
            if key == "Status":
                return c.status
            if key == "Priority":
                return c.priority
            if key == "Type":
                return c.case_type
            if key == "Worker":
                return c.assigned_worker.lower()
            if key == "Created":
                return c.created_at
            if key == "Incident":
                return c.incident_date
            return c.case_id

        return sorted(cases, key=k, reverse=descending)

    def unique_workers(self) -> List[str]:
        return sorted({c.assigned_worker for c in self.cases if c.assigned_worker.strip()})

    # ---------------- Reports ----------------
    def summary_report(self) -> Dict[str, object]:
        total = len(self.cases)
        by_status = Counter(c.status for c in self.cases)
        by_priority = Counter(c.priority for c in self.cases)
        by_type = Counter(c.case_type for c in self.cases)
        by_worker = Counter(c.assigned_worker for c in self.cases if c.assigned_worker.strip())

        open_cases = [c for c in self.cases if c.status not in ("Resolved", "Closed")]
        days = [c.days_open() for c in open_cases]
        days = [d for d in days if d is not None]
        avg_days_open = round(sum(days) / len(days), 2) if days else 0.0

        newest = sorted(self.cases, key=lambda c: c.created_at, reverse=True)[:5]

        return {
            "total": total,
            "open_count": len(open_cases),
            "avg_days_open": avg_days_open,
            "by_status": dict(by_status),
            "by_priority": dict(by_priority),
            "by_type": dict(by_type),
            "top_workers": by_worker.most_common(5),
            "newest_cases": newest,
        }