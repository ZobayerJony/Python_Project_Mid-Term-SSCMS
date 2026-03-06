from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from sscms.config import VALID_CASE_TYPES, VALID_PRIORITIES, VALID_STATUSES
from sscms.ui.theme import font_body
from sscms.ui.widgets import SectionHeader


class CasesView(ctk.CTkFrame):
    """
    Cases list view:
    - Search box
    - Filters
    - Sort controls
    - Table
    - Actions: New/Edit/Details/Delete/Refresh
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app

        self.search_var = tk.StringVar(value="")
        self.filter_status = tk.StringVar(value="All")
        self.filter_priority = tk.StringVar(value="All")
        self.filter_type = tk.StringVar(value="All")
        self.filter_worker = tk.StringVar(value="All")

        self.sort_key = tk.StringVar(value="ID")
        self.sort_desc = tk.BooleanVar(value=False)

        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Cases",
            subtitle="Search, filter, sort and manage survivor support cases.",
            right_text="New Case",
            right_command=self._new_case,
        )
        header.pack(fill="x", padx=14, pady=(14, 10))

        bar = ctk.CTkFrame(self, corner_radius=14)
        bar.pack(fill="x", padx=14, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            bar,
            textvariable=self.search_var,
            placeholder_text="Search by ID / name / phone / notes / worker...",
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=12)
        self.search_entry.bind("<Return>", lambda _e: self.refresh())

        ctk.CTkButton(bar, text="Search", command=self.refresh).pack(side="left", padx=8, pady=12)
        ctk.CTkButton(bar, text="Clear", fg_color=("gray75", "gray30"), command=self._clear).pack(
            side="left", padx=(0, 12), pady=12
        )

        row = ctk.CTkFrame(self, corner_radius=14)
        row.pack(fill="x", padx=14, pady=(0, 10))

        def dd(parent, title: str, var: tk.StringVar, values: list[str], width=150):
            box = ctk.CTkFrame(parent, corner_radius=12)
            box.pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(box, text=title, font=font_body()).pack(anchor="w", padx=10, pady=(8, 2))
            opt = ctk.CTkOptionMenu(box, variable=var, values=values, width=width, command=lambda _v: self.refresh())
            opt.pack(padx=10, pady=(0, 10))
            return opt

        dd(row, "Status", self.filter_status, ["All", *VALID_STATUSES])
        dd(row, "Priority", self.filter_priority, ["All", *VALID_PRIORITIES])
        dd(row, "Case Type", self.filter_type, ["All", *VALID_CASE_TYPES])
        self.worker_menu = dd(row, "Worker", self.filter_worker, ["All"], width=170)

        sort_box = ctk.CTkFrame(row, corner_radius=12)
        sort_box.pack(side="right", padx=10, pady=10)
        ctk.CTkLabel(sort_box, text="Sort", font=font_body()).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkOptionMenu(
            sort_box,
            variable=self.sort_key,
            values=["ID", "Name", "Status", "Priority", "Type", "Worker", "Created", "Incident"],
            command=lambda _v: self.refresh(),
            width=160,
        ).pack(padx=10, pady=(0, 6))
        ctk.CTkCheckBox(sort_box, text="Descending", variable=self.sort_desc, command=self.refresh).pack(
            padx=10, pady=(0, 10)
        )

        wrap = ctk.CTkFrame(self, corner_radius=14)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        columns = ("ID", "Name", "Phone", "Type", "Priority", "Status", "Worker", "Incident", "Created")
        self.tree = ttk.Treeview(wrap, columns=columns, show="headings", height=14)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130 if col not in ("Name", "Worker") else 180, anchor="w")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Priority", width=95, anchor="center")
        self.tree.column("Status", width=120, anchor="center")
        self.tree.column("Incident", width=110, anchor="center")
        self.tree.column("Created", width=110, anchor="center")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        vsb.pack(side="right", fill="y", padx=(0, 12), pady=12)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda _e: self._open_details())

        actions = ctk.CTkFrame(self, corner_radius=14)
        actions.pack(fill="x", padx=14, pady=(0, 14))

        ctk.CTkButton(actions, text="Details", command=self._open_details).pack(side="left", padx=12, pady=12)
        ctk.CTkButton(actions, text="Edit", command=self._edit_selected).pack(side="left", padx=8, pady=12)
        ctk.CTkButton(actions, text="Delete", fg_color="#B00020", command=self._delete_selected).pack(
            side="left", padx=8, pady=12
        )
        ctk.CTkButton(actions, text="Refresh", fg_color=("gray75", "gray30"), command=self.refresh).pack(
            side="right", padx=12, pady=12
        )

        self.refresh()

    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self._refresh_worker_values()

        query = self.search_var.get()
        base = self.app.manager.search(query)

        filtered = self.app.manager.filter_cases(
            base,
            status=self.filter_status.get(),
            priority=self.filter_priority.get(),
            case_type=self.filter_type.get(),
            worker=self.filter_worker.get(),
        )

        sorted_cases = self.app.manager.sort_cases(
            filtered,
            key=self.sort_key.get(),
            descending=bool(self.sort_desc.get()),
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in sorted_cases:
            self.tree.insert(
                "",
                "end",
                values=(
                    c.case_id,
                    c.survivor_name,
                    c.phone,
                    c.case_type,
                    c.priority,
                    c.status,
                    c.assigned_worker,
                    c.incident_date,
                    c.created_at,
                ),
            )

        self.app.status.set_left(f"Cases: {len(sorted_cases)} shown / {len(self.app.manager.cases)} total")

    def focus_search(self) -> None:
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")

    def _refresh_worker_values(self) -> None:
        workers = self.app.manager.unique_workers()
        values = ["All", *workers] if workers else ["All"]
        self.worker_menu.configure(values=values)
        if self.filter_worker.get() not in values:
            self.filter_worker.set("All")

    def _on_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            self.app.set_selected_case(None)
            return
        row = self.tree.item(sel[0]).get("values", [])
        if row:
            self.app.set_selected_case(int(row[0]))

    def _clear(self) -> None:
        self.search_var.set("")
        self.filter_status.set("All")
        self.filter_priority.set("All")
        self.filter_type.set("All")
        self.filter_worker.set("All")
        self.sort_key.set("ID")
        self.sort_desc.set(False)
        self.refresh()

    def _new_case(self) -> None:
        self.app.set_selected_case(None)
        form_view = self.app.views.get("form")
        if form_view and hasattr(form_view, "_reset"):
            form_view._reset()
        self.app.show_view("form")

    def _edit_selected(self) -> None:
        if self.app.selected_case_id is None:
            messagebox.showinfo("No selection", "Please select a case first.")
            return
        self.app.show_view("form")

    def _open_details(self) -> None:
        if self.app.selected_case_id is None:
            messagebox.showinfo("No selection", "Please select a case first.")
            return
        self.app.show_view("detail")

    def _delete_selected(self) -> None:
        cid = self.app.selected_case_id
        if cid is None:
            messagebox.showinfo("No selection", "Please select a case first.")
            return

        case = self.app.manager.get_by_id(cid)
        if not case:
            messagebox.showerror("Not found", "Selected case no longer exists.")
            self.refresh()
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete case #{cid}?\nThis cannot be undone."):
            return

        ok, msg = self.app.manager.delete_case(cid)
        if ok:
            self.app.set_selected_case(None)
            messagebox.showinfo("Deleted", msg)
            self.refresh()
            self.app.refresh_all()
        else:
            messagebox.showerror("Delete failed", msg)