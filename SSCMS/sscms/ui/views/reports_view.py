from __future__ import annotations

import customtkinter as ctk

from sscms.ui.theme import font_h2, font_body
from sscms.ui.widgets import SectionHeader


class ReportsView(ctk.CTkFrame):
    """
    Reports dashboard (summary):
    - totals
    - breakdown by status/priority/type
    - top workers
    - average days open
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Reports",
            subtitle="Summary statistics generated from stored cases.",
            right_text="Refresh",
            right_command=self.refresh,
        )
        header.pack(fill="x", padx=14, pady=(14, 10))

        wrap = ctk.CTkFrame(self, corner_radius=14)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.text = ctk.CTkTextbox(wrap, corner_radius=12)
        self.text.pack(fill="both", expand=True, padx=14, pady=14)

        self.refresh()

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        rep = self.app.manager.summary_report()

        def fmt_counter(title: str, d: dict) -> str:
            if not d:
                return f"{title}: (none)\n"
            lines = [f"{title}:"]
            for k, v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0])):
                lines.append(f"  - {k}: {v}")
            return "\n".join(lines) + "\n"

        lines = []
        lines.append("SSCMS — Summary Reports\n")
        lines.append(f"Total cases: {rep['total']}")
        lines.append(f"Open (not Resolved/Closed): {rep['open_count']}")
        lines.append(f"Average days open (open cases): {rep['avg_days_open']}\n")

        lines.append(fmt_counter("Cases by Status", rep["by_status"]))        # type: ignore[arg-type]
        lines.append(fmt_counter("Cases by Priority", rep["by_priority"]))    # type: ignore[arg-type]
        lines.append(fmt_counter("Cases by Case Type", rep["by_type"]))       # type: ignore[arg-type]

        lines.append("Top 5 Assigned Workers:")
        top_workers = rep["top_workers"]  # type: ignore[assignment]
        if top_workers:
            for w, n in top_workers:
                lines.append(f"  - {w}: {n}")
        else:
            lines.append("  (none)")
        lines.append("")

        lines.append("5 Most Recently Created Cases:")
        newest = rep["newest_cases"]  # type: ignore[assignment]
        if newest:
            for c in newest:
                lines.append(f"  - #{c.case_id} | {c.survivor_name} | {c.status} | Created: {c.created_at}")
        else:
            lines.append("  (none)")

        self.text.delete("1.0", "end")
        self.text.insert("1.0", "\n".join(lines))
        self.app.status.set_left("Reports updated")