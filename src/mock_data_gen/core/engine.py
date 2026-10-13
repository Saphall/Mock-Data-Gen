"""Turns a dataset spec (schema columns or a named generator) into batches of rows."""

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Protocol

from ..generators import GENERATORS
from .fields import FIELD_TYPES, Producer, build_producer, fake


class Generator(Protocol):
    column_names: list[str]
    tick_based: bool

    def batch(self, n: int, now: datetime) -> list[dict]: ...


class SchemaGenerator:
    tick_based = False

    def __init__(self, columns: list[dict]):
        cleaned = [c for c in columns if str(c.get("name") or "").strip()]
        if not cleaned:
            raise ValueError("schema needs at least one named column")
        names = [c["name"].strip() for c in cleaned]
        if len(set(names)) != len(names):
            raise ValueError("column names must be unique")
        self.column_names = names
        self._producers: list[tuple[str, Producer]] = [
            (c["name"].strip(), build_producer(c.get("type") or "", c.get("options") or "", float(c.get("null_pct") or 0)))
            for c in cleaned
        ]

    def batch(self, n: int, now: datetime) -> list[dict]:
        return [{name: produce(now) for name, produce in self._producers} for _ in range(n)]


def build_generator(spec: dict) -> Generator:
    if spec.get("kind") == "generator":
        entry = GENERATORS.get(spec.get("generator"))
        if entry is None:
            raise ValueError(f"unknown generator: {spec.get('generator')}")
        return entry["factory"]({**entry["defaults"], **spec.get("options", {})})
    return SchemaGenerator(spec.get("columns", []))


def seed_all(seed: int | None) -> None:
    if seed is None:
        return
    random.seed(seed)
    fake.seed_instance(seed)


def generate_rows(gen: Generator, rows: int, eps: int, end: datetime | None = None) -> list[dict]:
    """Produce `rows` rows as if generated at `eps` rows per second, the last second ending at `end`."""
    end = end or datetime.now(timezone.utc)
    eps = max(eps, 1)
    ticks = math.ceil(rows / eps)
    out: list[dict] = []
    for i in range(ticks):
        out.extend(gen.batch(min(eps, rows - i * eps) if not gen.tick_based else eps,
                             end - timedelta(seconds=ticks - 1 - i)))
    if gen.tick_based:
        out.sort(key=lambda r: r["timestamp"])
    return out[:rows]


def validate_schema(columns: list[dict]) -> list[str]:
    errors = []
    for c in columns:
        if str(c.get("name") or "").strip() and c.get("type") not in FIELD_TYPES:
            errors.append(f"{c.get('name')}: unknown type '{c.get('type')}'")
    return errors
