from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from sscms.config import ADMIN_USERNAME, ADMIN_PASSWORD, APP_NAME


class LoginView(ctk.CTkFrame):
    """
    Professional admin login screen for SSCMS.
    Left side: branding / overview
    Right side: modern login card
    """

    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        left = ctk.CTkFrame(self, corner_radius=0, fg_color=("#EAF4FF", "#0F172A"))
        left.grid(row=0, column=0, sticky="nsew")

        content = ctk.CTkFrame(left, fg_color="transparent")
        content.place(relx=0.08, rely=0.5, anchor="w")

        badge = ctk.CTkLabel(
            content,
            text=" ADMIN PORTAL ",
            corner_radius=20,
            fg_color=("#D6E9FF", "#1E293B"),
            text_color=("#0F172A", "#E2E8F0"),
            padx=14,
            pady=6,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        badge.pack(anchor="w", pady=(0, 20))

        title = ctk.CTkLabel(
            content,
            text="Survivor Support\nand Case Management\nSystem",
            justify="left",
            font=ctk.CTkFont(size=34, weight="bold"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            content,
            text=(
                "Securely manage survivor cases, monitor progress,\n"
                "track follow-ups, generate reports, and export data\n"
                "from one professional desktop interface."
            ),
            justify="left",
            text_color=("gray30", "gray75"),
            font=ctk.CTkFont(size=15),
        )
        subtitle.pack(anchor="w", pady=(18, 28))

        points_box = ctk.CTkFrame(
            content,
            corner_radius=20,
            fg_color=("#FFFFFF", "#111827"),
            width=500,
            height=220,
        )
        points_box.pack(anchor="w", fill="x", expand=False)
        points_box.pack_propagate(False)

        heading = ctk.CTkLabel(
            points_box,
            text="What the admin can do",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        heading.pack(anchor="w", padx=22, pady=(22, 14))

        for item in [
            "• Create and manage survivor support cases",
            "• Search, filter, and update case records",
            "• Track follow-up activities and case progress",
            "• View reports and export records to CSV",
        ]:
            lbl = ctk.CTkLabel(
                points_box,
                text=item,
                justify="left",
                anchor="w",
                font=ctk.CTkFont(size=14),
                text_color=("gray25", "gray80"),
            )
            lbl.pack(anchor="w", padx=22, pady=4)

        footer = ctk.CTkLabel(
            content,
            text="SSCMS • Midterm Project • Desktop GUI Application",
            text_color=("gray35", "gray70"),
            font=ctk.CTkFont(size=12),
        )
        footer.pack(anchor="w", pady=(24, 0))

    def _build_right_panel(self) -> None:
        right = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F8FAFC", "#020617"))
        right.grid(row=0, column=1, sticky="nsew")

        card = ctk.CTkFrame(
            right,
            corner_radius=24,
            fg_color=("#FFFFFF", "#0F172A"),
            width=390,
            height=470,
            border_width=1,
            border_color=("#DDE7F3", "#1E293B"),
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text="🔐",
            font=ctk.CTkFont(size=32),
        ).pack(pady=(34, 10))

        ctk.CTkLabel(
            card,
            text="Admin Login",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack()

        ctk.CTkLabel(
            card,
            text="Sign in to access the SSCMS dashboard",
            text_color=("gray40", "gray70"),
            font=ctk.CTkFont(size=13),
        ).pack(pady=(8, 22))

        ctk.CTkLabel(
            card,
            text="Username",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(fill="x", padx=32, pady=(0, 6))

        self.username_entry = ctk.CTkEntry(
            card,
            height=38,
            textvariable=self.username_var,
            placeholder_text="Enter admin username",
            corner_radius=10,
        )
        self.username_entry.pack(fill="x", padx=32, pady=(0, 16))

        ctk.CTkLabel(
            card,
            text="Password",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(fill="x", padx=32, pady=(0, 6))

        pass_row = ctk.CTkFrame(card, fg_color="transparent")
        pass_row.pack(fill="x", padx=32, pady=(0, 10))

        self.password_entry = ctk.CTkEntry(
            pass_row,
            height=38,
            textvariable=self.password_var,
            placeholder_text="Enter password",
            show="*",
            corner_radius=10,
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Return>", lambda _e: self._login())

        self.show_btn = ctk.CTkButton(
            pass_row,
            text="Show",
            width=68,
            height=38,
            corner_radius=10,
            command=self._toggle_password,
        )
        self.show_btn.pack(side="left", padx=(8, 0))

        remember_row = ctk.CTkFrame(card, fg_color="transparent")
        remember_row.pack(fill="x", padx=32, pady=(0, 18))

        remember = ctk.CTkCheckBox(
            remember_row,
            text="Show password",
            variable=self.show_password_var,
            command=self._toggle_password_from_checkbox,
        )
        remember.pack(side="left")

        ctk.CTkButton(
            card,
            text="Login to Dashboard",
            height=42,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._login,
        ).pack(fill="x", padx=32, pady=(2, 18))

        ctk.CTkLabel(
            card,
            text=APP_NAME,
            text_color=("gray45", "gray70"),
            font=ctk.CTkFont(size=11),
        ).pack(pady=(8, 0))

        self.username_entry.focus_set()

    def _toggle_password(self) -> None:
        current = self.password_entry.cget("show")
        if current == "*":
            self.password_entry.configure(show="")
            self.show_btn.configure(text="Hide")
            self.show_password_var.set(True)
        else:
            self.password_entry.configure(show="*")
            self.show_btn.configure(text="Show")
            self.show_password_var.set(False)

    def _toggle_password_from_checkbox(self) -> None:
        if self.show_password_var.get():
            self.password_entry.configure(show="")
            self.show_btn.configure(text="Hide")
        else:
            self.password_entry.configure(show="*")
            self.show_btn.configure(text="Show")

    def _login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Input", "Please enter both username and password.")
            return

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.app.show_main_app()
            return

        messagebox.showerror("Login Failed", "Invalid username or password.")