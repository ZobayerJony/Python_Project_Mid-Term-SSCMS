from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from sscms.config import ADMIN_USERNAME, ADMIN_PASSWORD, APP_NAME


class LoginView(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._build()

    def _build(self) -> None:
        self.pack_propagate(False)

        outer = ctk.CTkFrame(self, corner_radius=18)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            outer,
            text="Admin Login",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(padx=40, pady=(30, 10))

        subtitle = ctk.CTkLabel(
            outer,
            text=APP_NAME,
            text_color=("gray35", "gray75"),
            font=ctk.CTkFont(size=13),
        )
        subtitle.pack(padx=40, pady=(0, 20))

        username_entry = ctk.CTkEntry(
            outer,
            width=280,
            textvariable=self.username_var,
            placeholder_text="Username",
        )
        username_entry.pack(padx=40, pady=8)

        password_entry = ctk.CTkEntry(
            outer,
            width=280,
            textvariable=self.password_var,
            placeholder_text="Password",
            show="*",
        )
        password_entry.pack(padx=40, pady=8)
        password_entry.bind("<Return>", lambda _e: self._login())

        login_btn = ctk.CTkButton(
            outer,
            text="Login",
            width=280,
            command=self._login,
        )
        login_btn.pack(padx=40, pady=(16, 10))

        demo_info = ctk.CTkLabel(
            outer,
            text="Demo Login\nUsername: admin\nPassword: 1234",
            justify="center",
            text_color=("gray35", "gray75"),
            font=ctk.CTkFont(size=12),
        )
        demo_info.pack(padx=40, pady=(0, 25))

        username_entry.focus_set()

    def _login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.app.show_main_app()
            return

        messagebox.showerror("Login Failed", "Invalid username or password.")