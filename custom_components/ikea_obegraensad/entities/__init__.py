"""Entity framework for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from .base import IkeaLedBaseEntity
from .registry import EntityRegistry

__all__ = [
    "IkeaLedBaseEntity",
    "EntityRegistry",
]