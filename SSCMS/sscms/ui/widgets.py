from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from sscms.ui.theme import font_body, font_h2


class SectionHeader(ctk.CTkFrame):
    """
    Reusable section header: title + optional subtitle + optional right-side action button.
    """
    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        right_text: str = "",
        right_command: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        # IMPORTANT:
        # Do NOT hardcode corner_radius here if caller may pass it.
        # We'll set a default only if not provided.
        if "corner_radius" not in kwargs:
            kwargs["corner_radius"] = 14

        super().__init__(master, **kwargs)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=14, pady=12)

        ctk.CTkLabel(left, text=title, font=font_h2()).pack(anchor="w")
        if subtitle.strip():
            ctk.CTkLabel(
                left,
                text=subtitle,
                font=font_body(),
                text_color=("gray35", "gray75"),
            ).pack(anchor="w", pady=(2, 0))

        if right_text and right_command:
            ctk.CTkButton(self, text=right_text, command=right_command).pack(
                side="right", padx=14, pady=12
            )


class StatusBar(ctk.CTkFrame):
    """
    Bottom status bar: left status text + right helper text.
    """
    def __init__(self, master, **kwargs):
        # IMPORTANT FIX:
        # Previously we passed corner_radius twice (one here + one from caller).
        # Now we only accept what caller sends, and set default only if missing.
        if "corner_radius" not in kwargs:
            kwargs["corner_radius"] = 14

        super().__init__(master, **kwargs)

        self.left_var = tk.StringVar(value="Ready")
        self.right_var = tk.StringVar(value="")

        self.left = ctk.CTkLabel(self, textvariable=self.left_var, font=font_body())
        self.left.pack(side="left", padx=14, pady=10)

        self.right = ctk.CTkLabel(
            self,
            textvariable=self.right_var,
            font=font_body(),
            text_color=("gray35", "gray75"),
        )
        self.right.pack(side="right", padx=14, pady=10)

    def set_left(self, text: str) -> None:
        self.left_var.set(text)

    def set_right(self, text: str) -> None:
        self.right_var.set(text)


# minor update for git commit