"""Typed, local-first records used by the application."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    """UTC timestamp for persisted records."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass(slots=True)
class Investigation:
    id: str
    title: str
    target_type: str
    target_value: str
    case_ref: str
    created_at: str
    updated_at: str
    status: str = "Active"
    targets: dict[str, str] = field(default_factory=dict)
    purpose: str = ""
    authorization_note: str = ""
    notes: list[str] = field(default_factory=list)
    checklist: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        title: str,
        target_type: str,
        target_value: str,
        case_ref: str,
        *,
        targets: dict[str, str] | None = None,
        purpose: str = "",
        authorization_note: str = "",
    ) -> "Investigation":
        timestamp = utc_now()
        return cls(
            id=new_id("inv"),
            title=title.strip() or f"{target_type.title()} investigation",
            target_type=target_type,
            target_value=target_value.strip(),
            case_ref=case_ref.strip(),
            created_at=timestamp,
            updated_at=timestamp,
            targets=targets or {target_type: target_value.strip()},
            purpose=purpose.strip(),
            authorization_note=authorization_note.strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Investigation":
        # Records created before the richer case metadata existed.
        value.setdefault("targets", {value.get("target_type", "target"): value.get("target_value", "")})
        value.setdefault("purpose", "")
        value.setdefault("authorization_note", "")
        return cls(**value)


@dataclass(frozen=True, slots=True)
class Dork:
    id: str
    platform: str
    category: str
    priority: str
    query: str
    rationale: str


@dataclass(frozen=True, slots=True)
class ToolkitItem:
    id: str
    name: str
    description: str
    category: str
    supported_inputs: list[str]
    official_website: str
    homepage: str
    search_url: str | None
    pricing: str
    login_required: bool
    api_available: bool
    rating: float
    logo: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ToolkitItem":
        return cls(**value)


@dataclass(slots=True)
class Bookmark:
    id: str
    item_type: str
    title: str
    payload: dict[str, Any]
    created_at: str

    @classmethod
    def create(cls, item_type: str, title: str, payload: dict[str, Any]) -> "Bookmark":
        return cls(new_id("bm"), item_type, title, payload, utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Bookmark":
        return cls(**value)
