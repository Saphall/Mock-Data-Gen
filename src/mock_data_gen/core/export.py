"""Serialisation of rows to CSV, JSON, JSONL and SQL INSERT statements."""

import csv
import io
import json
import re
from typing import Any, Iterable

FORMATS = {"csv": "text/csv", "json": "application/json", "jsonl": "application/x-ndjson", "sql": "application/sql"}
APPENDABLE = {"csv", "jsonl", "sql"}


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name.strip()).strip("_").lower() or "dataset"


def _sql_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def to_csv(rows: Iterable[dict], columns: list[str], header: bool = True) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    if header:
        writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def to_jsonl(rows: Iterable[dict]) -> str:
    return "".join(json.dumps(r, default=str) + "\n" for r in rows)


def to_sql(rows: Iterable[dict], columns: list[str], table: str) -> str:
    table = safe_name(table)
    cols = ", ".join(f'"{c}"' for c in columns)
    return "".join(
        f'INSERT INTO "{table}" ({cols}) VALUES ({", ".join(_sql_value(r.get(c)) for c in columns)});\n'
        for r in rows
    )


def serialize(rows: list[dict], columns: list[str], fmt: str, table: str = "dataset", header: bool = True) -> str:
    if fmt == "csv":
        return to_csv(rows, columns, header)
    if fmt == "json":
        return json.dumps(rows, default=str, indent=2)
    if fmt == "jsonl":
        return to_jsonl(rows)
    if fmt == "sql":
        return to_sql(rows, columns, table)
    raise ValueError(f"unsupported format: {fmt}")
