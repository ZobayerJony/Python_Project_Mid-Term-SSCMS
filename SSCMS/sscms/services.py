from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from sscms.config import EXPORT_DIR
from sscms.models import SurvivorCase


@dataclass
class ExportService:
    """
    Service layer: export cases to CSV inside data/exports/.
    """
    export_dir: Path = EXPORT_DIR

    def ensure_dir(self) -> None:
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_cases_csv(self, cases: List[SurvivorCase]) -> Tuple[bool, str, Path | None]:
        self.ensure_dir()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = self.export_dir / f"sscms_cases_{ts}.csv"

        try:
            with out_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["case_id", "survivor_name", "phone", "case_type", "priority", "status",
                     "assigned_worker", "incident_date", "created_at", "notes", "activity_count"]
                )
                for c in cases:
                    writer.writerow(
                        [
                            c.case_id, c.survivor_name, c.phone, c.case_type, c.priority, c.status,
                            c.assigned_worker, c.incident_date, c.created_at,
                            c.notes.replace("\n", " ").strip(),
                            len(c.activities),
                        ]
                    )
            return True, f"Exported {len(cases)} cases to CSV.", out_path
        except Exception as e:
            return False, f"Export failed: {e}", None


