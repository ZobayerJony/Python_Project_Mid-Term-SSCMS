from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from sscms.models import SurvivorCase


@dataclass
class JsonStore:
    """
    JSON persistence with corruption-safe backup.

    Schema:
    {
      "next_id": 1,
      "cases": [ ... ]
    }
    """
    path: Path

    def ensure(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_raw(self) -> Dict[str, Any]:
        self.ensure()
        if not self.path.exists():
            default = {"next_id": 1, "cases": []}
            self.save_raw(default)
            return default

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if "next_id" not in data or "cases" not in data:
                raise ValueError("Invalid schema")
            return data
        except Exception:
            backup = self.path.with_suffix(".backup.json")
            try:
                self.path.replace(backup)
            except Exception:
                pass
            default = {"next_id": 1, "cases": []}
            self.save_raw(default)
            return default

    def save_raw(self, data: Dict[str, Any]) -> None:
        self.ensure()
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_cases(self) -> Dict[str, Any]:
        raw = self.load_raw()
        cases = [SurvivorCase.from_dict(c) for c in raw.get("cases", [])]
        return {"next_id": int(raw.get("next_id", 1)), "cases": cases}

    def save_cases(self, next_id: int, cases: List[SurvivorCase]) -> None:
        raw = {"next_id": next_id, "cases": [c.to_dict() for c in cases]}
        self.save_raw(raw)