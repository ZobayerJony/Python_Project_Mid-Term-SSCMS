from __future__ import annotations

import customtkinter as ctk


def apply_theme() -> None:
    """
    Apply consistent theme across the app.
    You can change appearance mode to "Dark" / "Light" / "System".
    """
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")


def font_title():
    return ctk.CTkFont(size=20, weight="bold")


def font_h2():
    return ctk.CTkFont(size=16, weight="bold")


def font_body():
    return ctk.CTkFont(size=13)


def font_mono():
    return ctk.CTkFont(size=12, family="Consolas")


