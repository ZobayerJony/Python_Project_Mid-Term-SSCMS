from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from sscms.ui.widgets import SectionHeader


class ExportView(ctk.CTkFrame):
    """
    Export view:
    - Exports ALL cases to CSV using ExportService
    (Exports saved into data/exports/)
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Export (CSV)",
            subtitle="Export case records to CSV for external reporting.",
            right_text="Export Now",
            right_command=self._export_all,
        )
        header.pack(fill="x", padx=14, pady=(14, 10))

        wrap = ctk.CTkFrame(self, corner_radius=14)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.box = ctk.CTkTextbox(wrap, corner_radius=12)
        self.box.pack(fill="both", expand=True, padx=14, pady=14)
        self.box.insert(
            "1.0",
            "Export Notes:\n"
            "• This will export ALL stored cases to a CSV file.\n"
            "• Output location: data/exports/\n"
            "• CSV includes: case fields + activity_count.\n\n"
            "Click 'Export Now' to generate a CSV file.\n"
        )
        self.box.configure(state="disabled")

    def on_show(self) -> None:
        self.app.status.set_left("Ready to export")

    def _export_all(self) -> None:
        ok, msg, path = self.app.export_service.export_cases_csv(self.app.manager.cases)
        if ok:
            messagebox.showinfo("Exported", f"{msg}\n\nSaved to:\n{path}")
            self.app.status.set_left("Export completed")
        else:
            messagebox.showerror("Export failed", msg)
            self.app.status.set_left("Export failed")


