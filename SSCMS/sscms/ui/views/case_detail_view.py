from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from sscms.config import VALID_STATUSES
from sscms.ui.theme import font_body, font_h2, font_mono
from sscms.ui.widgets import SectionHeader


class CaseDetailView(ctk.CTkFrame):
    """
    Detail page:
    - Shows selected case info
    - Shows activity timeline
    - Quick actions: change status, add follow-up note, edit
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app

        self.status_var = tk.StringVar(value=VALID_STATUSES[0])
        self._build()

    def _build(self) -> None:
        self.header = SectionHeader(
            self,
            title="Case Details",
            subtitle="View full case information and timeline activities.",
            right_text="Back to Cases",
            right_command=lambda: self.app.show_view("cases"),
        )
        self.header.pack(fill="x", padx=14, pady=(14, 10))

        body = ctk.CTkFrame(self, corner_radius=14)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # Left: info
        left = ctk.CTkFrame(body, corner_radius=14)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(14, 7), pady=14)
        ctk.CTkLabel(left, text="Case Summary", font=font_h2()).pack(anchor="w", padx=14, pady=(14, 8))

        self.info = ctk.CTkTextbox(left, corner_radius=12)
        self.info.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.info.configure(state="disabled")

        # Right top: quick actions
        right_top = ctk.CTkFrame(body, corner_radius=14)
        right_top.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=(14, 7))

        ctk.CTkLabel(right_top, text="Quick Actions", font=font_h2()).pack(anchor="w", padx=14, pady=(14, 8))

        row = ctk.CTkFrame(right_top, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(row, text="Change Status:", font=font_body()).pack(side="left")
        self.status_menu = ctk.CTkOptionMenu(row, variable=self.status_var, values=list(VALID_STATUSES))
        self.status_menu.pack(side="left", padx=10)

        ctk.CTkButton(right_top, text="Apply Status", command=self._apply_status).pack(
            anchor="w", padx=14, pady=(0, 10)
        )
        ctk.CTkButton(right_top, text="Edit Case", command=lambda: self.app.show_view("form")).pack(
            anchor="w", padx=14, pady=(0, 14)
        )

        # Right bottom: timeline
        right_bottom = ctk.CTkFrame(body, corner_radius=14)
        right_bottom.grid(row=1, column=1, sticky="nsew", padx=(7, 14), pady=(7, 14))
        right_bottom.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_bottom, text="Activity Timeline", font=font_h2()).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 8)
        )

        self.timeline = ctk.CTkTextbox(right_bottom, corner_radius=12)
        self.timeline.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 10))

        self.follow = ctk.CTkTextbox(right_bottom, height=80, corner_radius=12)
        self.follow.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        self.follow.insert("1.0", "")
        ctk.CTkButton(right_bottom, text="Add Follow-up Note", command=self._add_follow_up).grid(
            row=3, column=0, sticky="w", padx=14, pady=(0, 14)
        )

    # hooks
    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        cid = self.app.selected_case_id
        if cid is None:
            self._set_text(self.info, "No case selected.\n\nGo to Cases and select one.")
            self._set_text(self.timeline, "")
            self.app.status.set_left("No case selected")
            return

        case = self.app.manager.get_by_id(cid)
        if not case:
            self._set_text(self.info, "Selected case no longer exists.")
            self._set_text(self.timeline, "")
            return

        self.status_var.set(case.status)

        summary = (
            f"Case ID: {case.case_id}\n"
            f"Survivor Name: {case.survivor_name}\n"
            f"Phone: {case.phone}\n"
            f"Case Type: {case.case_type}\n"
            f"Priority: {case.priority}\n"
            f"Status: {case.status}\n"
            f"Assigned Worker: {case.assigned_worker}\n"
            f"Incident Date: {case.incident_date}\n"
            f"Created At: {case.created_at}\n"
            f"Days Open: {case.days_open() if case.days_open() is not None else 'N/A'}\n\n"
            f"Notes:\n{case.notes or '(none)'}\n"
        )
        self._set_text(self.info, summary)

        # timeline
        lines = []
        for a in case.activities:
            lines.append(f"[{a.timestamp}] {a.action}\n{a.detail}\n")
            lines.append("-" * 42 + "\n")
        self._set_text(self.timeline, "".join(lines).strip())

        self.app.status.set_left(f"Viewing case #{cid}")

    # helpers
    def _set_text(self, box: ctk.CTkTextbox, text: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def _apply_status(self) -> None:
        cid = self.app.selected_case_id
        if cid is None:
            messagebox.showinfo("No selection", "Select a case first.")
            return
        case = self.app.manager.get_by_id(cid)
        if not case:
            messagebox.showerror("Not found", "Case not found.")
            return

        new_status = self.status_var.get()
        if new_status == case.status:
            messagebox.showinfo("No change", "Status is already set.")
            return

        ok, msg = self.app.manager.update_case(
            case_id=cid,
            survivor_name=case.survivor_name,
            phone=case.phone,
            case_type=case.case_type,
            priority=case.priority,
            status=new_status,
            assigned_worker=case.assigned_worker,
            incident_date=case.incident_date,
            notes=case.notes,
            add_activity_note=f"Status updated to '{new_status}'.",
        )
        if not ok:
            messagebox.showerror("Failed", msg)
            return

        messagebox.showinfo("Updated", msg)
        self.app.refresh_all()
        self.refresh()

    def _add_follow_up(self) -> None:
        cid = self.app.selected_case_id
        if cid is None:
            messagebox.showinfo("No selection", "Select a case first.")
            return
        case = self.app.manager.get_by_id(cid)
        if not case:
            messagebox.showerror("Not found", "Case not found.")
            return

        note = self.follow.get("1.0", "end").strip()
        if not note:
            messagebox.showinfo("Empty note", "Write a follow-up note first.")
            return

        ok, msg = self.app.manager.update_case(
            case_id=cid,
            survivor_name=case.survivor_name,
            phone=case.phone,
            case_type=case.case_type,
            priority=case.priority,
            status=case.status,
            assigned_worker=case.assigned_worker,
            incident_date=case.incident_date,
            notes=case.notes,
            add_activity_note=note,
        )
        if not ok:
            messagebox.showerror("Failed", msg)
            return

        self.follow.delete("1.0", "end")
        self.app.refresh_all()
        self.refresh()