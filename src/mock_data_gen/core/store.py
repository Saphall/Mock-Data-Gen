"""In-process dataset registry shared by the Streamlit UI and the HTTP API."""

import threading
import time
from collections import deque
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path

from ..config import OUTPUT_DIR
from .engine import Generator, build_generator, generate_rows, seed_all
from .export import APPENDABLE, FORMATS, safe_name, serialize

MAX_ROWS_ONCE = 1_000_000


class Dataset:
    def __init__(self, name: str, spec: dict, eps: int = 10, limit: int = -1, buffer: int = 100_000,
                 save: dict | None = None, seed: int | None = None):
        if save and save.get("format") not in FORMATS:
            raise ValueError(f"unsupported save format: {save.get('format')}")
        self.name = safe_name(name)
        self.spec = spec
        self.eps = max(int(eps), 1)
        self.limit = int(limit)
        self.save = save
        self.seed = seed
        self.generator: Generator = build_generator(spec)
        self.columns = list(self.generator.column_names)
        self.created_at = datetime.now(timezone.utc)
        self.total = 0
        self.last_error: str | None = None
        self.saved_path: str | None = None
        self._rows: deque[dict] = deque(maxlen=max(int(buffer), 1))
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def streaming(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _append(self, rows: list[dict], file_append: bool) -> None:
        with self._lock:
            self._rows.extend(rows)
            self.total += len(rows)
        if self.save and rows:
            self._write_file(rows, file_append)

    def _write_file(self, rows: list[dict], append: bool) -> None:
        fmt = self.save["format"]
        if append and fmt not in APPENDABLE:
            raise ValueError(f"'{fmt}' files cannot be appended to while streaming; use csv, jsonl or sql")
        path = Path(self.save.get("directory") or OUTPUT_DIR).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        path /= f"{self.name}.{fmt}"
        header = not (append and path.exists() and path.stat().st_size > 0)
        with path.open("a" if append else "w", encoding="utf-8", newline="") as fh:
            fh.write(serialize(rows, self.columns, fmt, self.name, header))
        self.saved_path = str(path)

    def generate(self, rows: int, replace: bool = True) -> int:
        rows = min(max(int(rows), 1), MAX_ROWS_ONCE)
        seed_all(self.seed)
        batch = generate_rows(self.generator, rows, self.eps)
        if replace:
            with self._lock:
                self._rows.clear()
                self.total = 0
        self._append(batch, file_append=not replace)
        return len(batch)

    def start_stream(self) -> None:
        if self.streaming:
            return
        seed_all(self.seed)
        self._stop.clear()
        self.last_error = None
        self._thread = threading.Thread(target=self._run, name=f"stream-{self.name}", daemon=True)
        self._thread.start()

    def stop_stream(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _run(self) -> None:
        emitted = 0
        while not self._stop.is_set():
            started = time.monotonic()
            want = self.eps if self.limit < 0 else min(self.eps, self.limit - emitted)
            if want <= 0:
                break
            try:
                batch = self.generator.batch(want, datetime.now(timezone.utc))
                if self.limit >= 0:
                    batch = batch[: self.limit - emitted]
                self._append(batch, file_append=True)
            except Exception as exc:  # surfaced via API/UI instead of killing the thread silently
                self.last_error = str(exc)
                break
            emitted += len(batch)
            if self.limit >= 0 and emitted >= self.limit:
                break
            self._stop.wait(max(0.0, 1.0 - (time.monotonic() - started)))

    def page(self, limit: int = 100, offset: int = 0, after: int | None = None) -> tuple[list[dict], int]:
        """Return (rows, cursor); pass the cursor as `after` to receive only newer rows."""
        with self._lock:
            data = list(self._rows)
            first_seq = self.total - len(data)
        if after is not None:
            offset = max(after - first_seq, 0)
        rows = data[offset: offset + max(limit, 0)]
        return rows, first_seq + offset + len(rows)

    def tail(self, cursor: int, limit: int = 500) -> tuple[list[dict], int]:
        """Rows generated after `cursor` (a total-rows count), oldest first, plus the new cursor.

        Cheap enough to poll at the buffer's tail; rows already evicted from the buffer are skipped.
        """
        with self._lock:
            total = self.total
            if cursor > total:  # the dataset was regenerated, so start over
                cursor = 0
            fresh = list(islice(reversed(self._rows), min(total - cursor, len(self._rows))))[::-1]
        batch = fresh[:limit]
        return batch, total - len(fresh) + len(batch)

    def all_rows(self) -> list[dict]:
        with self._lock:
            return list(self._rows)

    def info(self) -> dict:
        with self._lock:
            buffered = len(self._rows)
        return {
            "name": self.name,
            "columns": self.columns,
            "total_generated": self.total,
            "buffered_rows": buffered,
            "streaming": self.streaming,
            "eps": self.eps,
            "limit": self.limit,
            "save": self.save,
            "saved_path": self.saved_path,
            "created_at": self.created_at.isoformat(),
            "error": self.last_error,
        }


class Store:
    def __init__(self):
        self._datasets: dict[str, Dataset] = {}
        self._lock = threading.Lock()

    def put(self, dataset: Dataset) -> Dataset:
        with self._lock:
            old = self._datasets.get(dataset.name)
            self._datasets[dataset.name] = dataset
        if old:
            old.stop_stream()
        return dataset

    def get(self, name: str) -> Dataset | None:
        return self._datasets.get(safe_name(name))

    def delete(self, name: str) -> bool:
        with self._lock:
            dataset = self._datasets.pop(safe_name(name), None)
        if dataset:
            dataset.stop_stream()
        return dataset is not None

    def list(self) -> list[Dataset]:
        return list(self._datasets.values())


STORE = Store()
