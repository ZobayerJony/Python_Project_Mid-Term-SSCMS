from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from sscms.config import VALID_CASE_TYPES, VALID_PRIORITIES, VALID_STATUSES
from sscms.ui.theme import font_body
from sscms.ui.widgets import SectionHeader


class CaseFormView(ctk.CTkFrame):
    """
    Add/Edit form.
    - If app.selected_case_id is None -> Add mode
    - Else -> Edit mode
    - Bottom action buttons stay visible
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app

        self.v_case_id = tk.StringVar(value="Auto")
        self.v_name = tk.StringVar()
        self.v_phone = tk.StringVar()
        self.v_type = tk.StringVar(value=VALID_CASE_TYPES[0])
        self.v_priority = tk.StringVar(value=VALID_PRIORITIES[1])
        self.v_status = tk.StringVar(value=VALID_STATUSES[0])
        self.v_worker = tk.StringVar()
        self.v_incident = tk.StringVar()

        self._build()

    def _build(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = SectionHeader(
            self,
            title="Add / Edit Case",
            subtitle="Fill in the details carefully. All required fields are validated.",
            right_text="Back to Cases",
            right_command=lambda: self.app.show_view("cases"),
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 10))

        # Main body
        body = ctk.CTkFrame(self, corner_radius=14)
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        # Form area
        form = ctk.CTkFrame(body, corner_radius=14)
        form.grid(row=0, column=0, sticky="nsew", padx=14, pady=(14, 10))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        def label(text, r, c):
            ctk.CTkLabel(form, text=text, font=font_body()).grid(
                row=r, column=c, sticky="w", padx=12, pady=(12, 4)
            )

        def put(widget, r, c, colspan=1):
            widget.grid(row=r, column=c, columnspan=colspan, sticky="ew", padx=12, pady=(0, 6))

        label("Case ID", 0, 0)
        self.e_id = ctk.CTkEntry(form, textvariable=self.v_case_id, state="disabled")
        put(self.e_id, 1, 0)

        label("Incident Date (YYYY-MM-DD)", 0, 1)
        self.e_incident = ctk.CTkEntry(form, textvariable=self.v_incident, placeholder_text="YYYY-MM-DD")
        put(self.e_incident, 1, 1)

        label("Survivor Name *", 2, 0)
        put(ctk.CTkEntry(form, textvariable=self.v_name, placeholder_text="Full name"), 3, 0)

        label("Phone *", 2, 1)
        put(ctk.CTkEntry(form, textvariable=self.v_phone, placeholder_text="Digits, +, -, spaces"), 3, 1)

        label("Case Type *", 4, 0)
        put(ctk.CTkOptionMenu(form, variable=self.v_type, values=list(VALID_CASE_TYPES)), 5, 0)

        label("Priority *", 4, 1)
        put(ctk.CTkOptionMenu(form, variable=self.v_priority, values=list(VALID_PRIORITIES)), 5, 1)

        label("Status *", 6, 0)
        put(ctk.CTkOptionMenu(form, variable=self.v_status, values=list(VALID_STATUSES)), 7, 0)

        label("Assigned Worker *", 6, 1)
        put(ctk.CTkEntry(form, textvariable=self.v_worker, placeholder_text="Case worker name"), 7, 1)

        label("Case Notes", 8, 0)
        label("Follow-up Note (adds to timeline)", 8, 1)

        self.notes_box = ctk.CTkTextbox(form, height=140, corner_radius=10)
        self.notes_box.grid(row=9, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.follow_box = ctk.CTkTextbox(form, height=140, corner_radius=10)
        self.follow_box.grid(row=9, column=1, sticky="nsew", padx=12, pady=(0, 12))

        # Fixed bottom button row
        btns = ctk.CTkFrame(body, corner_radius=14)
        btns.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkButton(btns, text="Save", command=self._save).pack(side="left", padx=12, pady=12)
        ctk.CTkButton(btns, text="Reset", fg_color=("gray75", "gray30"), command=self._reset).pack(
            side="left", padx=8, pady=12
        )
        ctk.CTkButton(btns, text="Open Details", command=self._go_detail).pack(side="right", padx=12, pady=12)

        self._reset()

    def on_show(self) -> None:
        self._load_selected()

    def _reset(self) -> None:
        self.app.set_selected_case(None)
        self.v_case_id.set("Auto")
        self.v_name.set("")
        self.v_phone.set("")
        self.v_type.set(VALID_CASE_TYPES[0])
        self.v_priority.set(VALID_PRIORITIES[1])
        self.v_status.set(VALID_STATUSES[0])
        self.v_worker.set("")
        self.v_incident.set("")
        self.notes_box.delete("1.0", "end")
        self.follow_box.delete("1.0", "end")
        self.app.status.set_left("New case mode")

    def _load_selected(self) -> None:
        cid = self.app.selected_case_id
        if cid is None:
            self.v_case_id.set("Auto")
            self.follow_box.delete("1.0", "end")
            return

        case = self.app.manager.get_by_id(cid)
        if not case:
            messagebox.showerror("Not found", "Selected case no longer exists.")
            self._reset()
            self.app.show_view("cases")
            return

        self.v_case_id.set(str(case.case_id))
        self.v_name.set(case.survivor_name)
        self.v_phone.set(case.phone)
        self.v_type.set(case.case_type)
        self.v_priority.set(case.priority)
        self.v_status.set(case.status)
        self.v_worker.set(case.assigned_worker)
        self.v_incident.set(case.incident_date)
        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("1.0", case.notes)
        self.follow_box.delete("1.0", "end")
        self.app.status.set_left(f"Editing case #{cid}")

    def _save(self) -> None:
        cid_text = self.v_case_id.get().strip()
        notes = self.notes_box.get("1.0", "end").strip()
        follow = self.follow_box.get("1.0", "end").strip()

        if cid_text.isdigit():
            cid = int(cid_text)
            ok, msg = self.app.manager.update_case(
                case_id=cid,
                survivor_name=self.v_name.get(),
                phone=self.v_phone.get(),
                case_type=self.v_type.get(),
                priority=self.v_priority.get(),
                status=self.v_status.get(),
                assigned_worker=self.v_worker.get(),
                incident_date=self.v_incident.get(),
                notes=notes,
                add_activity_note=follow,
            )
            if not ok:
                messagebox.showwarning("Validation", msg)
                return

            messagebox.showinfo("Saved", msg)
            self.follow_box.delete("1.0", "end")
            self.app.refresh_all()
            self.app.show_view("cases")
            return

        ok, msg, created = self.app.manager.add_case(
            survivor_name=self.v_name.get(),
            phone=self.v_phone.get(),
            case_type=self.v_type.get(),
            priority=self.v_priority.get(),
            status=self.v_status.get(),
            assigned_worker=self.v_worker.get(),
            incident_date=self.v_incident.get(),
            notes=notes,
        )
        if not ok:
            messagebox.showwarning("Validation", msg)
            return

        new_id = created.case_id if created else None
        self.app.set_selected_case(new_id)
        messagebox.showinfo("Added", f"{msg}\nNew Case ID: {new_id}")
        self.app.refresh_all()
        self.app.show_view("cases")

    def _go_detail(self) -> None:
        if self.app.selected_case_id is None:
            messagebox.showinfo("No case selected", "Save the case first, then open details.")
            return
        self.app.show_view("detail")