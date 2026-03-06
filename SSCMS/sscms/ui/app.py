from __future__ import annotations

from typing import Dict

import customtkinter as ctk

from sscms.config import APP_NAME, DATA_FILE, DEFAULT_GEOMETRY, MIN_SIZE
from sscms.manager import CaseManager
from sscms.storage import JsonStore
from sscms.services import ExportService
from sscms.ui.theme import apply_theme, font_body, font_title
from sscms.ui.widgets import StatusBar

from sscms.ui.views.cases_view import CasesView
from sscms.ui.views.case_form_view import CaseFormView
from sscms.ui.views.case_detail_view import CaseDetailView
from sscms.ui.views.reports_view import ReportsView
from sscms.ui.views.export_view import ExportView


class SSCMSApp:
    """
    Main GUI controller.
    - Creates manager + services
    - Sidebar navigation
    - Loads views into a content frame
    - Provides shared app context (manager/services/status)
    """

    def __init__(self) -> None:
        apply_theme()

        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry(DEFAULT_GEOMETRY)
        self.root.minsize(MIN_SIZE[0], MIN_SIZE[1])

        self.manager = CaseManager(JsonStore(DATA_FILE))
        self.export_service = ExportService()

        self.selected_case_id: int | None = None

        self._build_shell()

        self.views: Dict[str, ctk.CTkFrame] = {}
        self._init_views()

        self.show_view("cases")

        self.root.bind("<Control-n>", lambda _e: self._shortcut_new_case())
        self.root.bind("<Control-f>", lambda _e: self._shortcut_focus_search())
        self.root.bind("<F5>", lambda _e: self.refresh_all())

    def run(self) -> None:
        self.root.mainloop()

    # ---------------- Layout Shell ----------------
    def _build_shell(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self.root, corner_radius=16, width=260)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(14, 10), pady=14)
        self.sidebar.grid_rowconfigure(10, weight=1)

        self.content = ctk.CTkFrame(self.root, corner_radius=16)
        self.content.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.status = StatusBar(self.root, corner_radius=16)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))

        self._build_sidebar_items()

    def _build_sidebar_items(self) -> None:
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=12, pady=(14, 8))

        ctk.CTkLabel(brand, text="SSCMS", font=font_title()).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="Survivor Support\nCase Management",
            font=font_body(),
            text_color=("gray35", "gray75"),
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        self.btn_cases = ctk.CTkButton(self.sidebar, text="Cases", command=lambda: self.show_view("cases"))
        self.btn_cases.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 6))

        self.btn_new = ctk.CTkButton(self.sidebar, text="Add / Edit Case", command=lambda: self._open_new_case_form())
        self.btn_new.grid(row=2, column=0, sticky="ew", padx=12, pady=6)

        self.btn_detail = ctk.CTkButton(self.sidebar, text="Case Details", command=lambda: self.show_view("detail"))
        self.btn_detail.grid(row=3, column=0, sticky="ew", padx=12, pady=6)

        self.btn_reports = ctk.CTkButton(self.sidebar, text="Reports", command=lambda: self.show_view("reports"))
        self.btn_reports.grid(row=4, column=0, sticky="ew", padx=12, pady=6)

        self.btn_export = ctk.CTkButton(self.sidebar, text="Export (CSV)", command=lambda: self.show_view("export"))
        self.btn_export.grid(row=5, column=0, sticky="ew", padx=12, pady=6)

        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.grid(row=10, column=0, sticky="nsew")

        help_box = ctk.CTkFrame(self.sidebar, corner_radius=14)
        help_box.grid(row=11, column=0, sticky="ew", padx=12, pady=(0, 12))

        ctk.CTkLabel(help_box, text="Shortcuts", font=font_body()).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(
            help_box,
            text="Ctrl+N: New Case\nCtrl+F: Search\nF5: Refresh",
            font=font_body(),
            text_color=("gray35", "gray75"),
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 10))

    # ---------------- Views ----------------
    def _init_views(self) -> None:
        self.views["cases"] = CasesView(self.content, app=self)
        self.views["form"] = CaseFormView(self.content, app=self)
        self.views["detail"] = CaseDetailView(self.content, app=self)
        self.views["reports"] = ReportsView(self.content, app=self)
        self.views["export"] = ExportView(self.content, app=self)

        for v in self.views.values():
            v.grid(row=0, column=0, sticky="nsew")

    def show_view(self, name: str) -> None:
        if name not in self.views:
            return

        self.views[name].tkraise()

        view = self.views[name]
        on_show = getattr(view, "on_show", None)
        if callable(on_show):
            on_show()

        self.status.set_left(f"Viewing: {name.capitalize()}")

    # ---------------- Shared Actions ----------------
    def set_selected_case(self, case_id: int | None) -> None:
        self.selected_case_id = case_id
        if case_id is None:
            self.status.set_right("No case selected")
        else:
            self.status.set_right(f"Selected Case ID: {case_id}")

    def refresh_all(self) -> None:
        for _, view in self.views.items():
            refresh = getattr(view, "refresh", None)
            if callable(refresh):
                refresh()
        self.status.set_left("Refreshed")

    def _open_new_case_form(self) -> None:
        self.set_selected_case(None)
        form_view = self.views.get("form")
        if form_view and hasattr(form_view, "_reset"):
            form_view._reset()
        self.show_view("form")
        self.status.set_left("New case mode")

    # ---------------- Shortcuts ----------------
    def _shortcut_new_case(self) -> None:
        self._open_new_case_form()

    def _shortcut_focus_search(self) -> None:
        view = self.views.get("cases")
        if not view:
            return
        focus_search = getattr(view, "focus_search", None)
        if callable(focus_search):
            self.show_view("cases")
            focus_search()
            self.status.set_left("Search focused")