"""Uploaders ke liye common types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UploadResult:
    platform: str
    ok: bool
    detail: str = ""

    def line(self) -> str:
        mark = "OK  " if self.ok else "FAIL"
        return f"[{self.platform:<9}] {mark} {self.detail}"
