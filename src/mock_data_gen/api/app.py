"""HTTP routes exposing generated datasets to other services."""

import asyncio
import json
import time

from fastapi import Body, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from ..core import FORMATS, MAX_ROWS_ONCE, STORE, Dataset, serialize

app = FastAPI(title="Mock Data Gen API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _dataset(name: str) -> Dataset:
    dataset = STORE.get(name)
    if dataset is None:
        raise HTTPException(404, f"dataset '{name}' not found")
    return dataset


@app.get("/")
def root() -> dict:
    return {"service": "mock-data-gen", "docs": "/docs", "datasets": [d.name for d in STORE.list()]}


@app.get("/datasets")
def list_datasets() -> list[dict]:
    return [d.info() for d in STORE.list()]


@app.post("/datasets", status_code=201)
def create_dataset(payload: dict = Body(...)) -> dict:
    """Body: {name, spec, rows?, eps?, limit?, stream?}. `spec` matches the UI schema format."""
    try:
        dataset = Dataset(payload["name"], payload["spec"], eps=payload.get("eps", 10),
                          limit=payload.get("limit", -1), seed=payload.get("seed"))
        if payload.get("rows"):
            dataset.generate(payload["rows"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, f"invalid dataset: {exc}") from exc
    STORE.put(dataset)
    if payload.get("stream"):
        dataset.start_stream()
    return dataset.info()


@app.get("/datasets/{name}")
def get_dataset(name: str) -> dict:
    dataset = _dataset(name)
    return {**dataset.info(), "spec": dataset.spec}


@app.delete("/datasets/{name}")
def delete_dataset(name: str) -> dict:
    return {"deleted": STORE.delete(name)}


@app.get("/datasets/{name}/rows")
def get_rows(name: str, limit: int = Query(100, ge=1, le=MAX_ROWS_ONCE), offset: int = Query(0, ge=0),
             after: int | None = Query(None, ge=0, description="cursor from a previous call; returns newer rows only"),
             format: str = Query("json")):
    dataset = _dataset(name)
    if format not in FORMATS:
        raise HTTPException(422, f"format must be one of {', '.join(FORMATS)}")
    rows, cursor = dataset.page(limit, offset, after)
    if format == "json":
        return {"name": dataset.name, "count": len(rows), "cursor": cursor, "data": rows}
    body = serialize(rows, dataset.columns, format, dataset.name)
    return Response(body, media_type=FORMATS[format], headers={"X-Cursor": str(cursor)})


@app.get("/datasets/{name}/stream")
async def follow(
    name: str,
    format: str = Query("ndjson", pattern="^(ndjson|sse)$", description="ndjson: one JSON row per line; sse: server-sent events"),
    start: str = Query("now", pattern="^(now|beginning)$", description="'beginning' replays the buffered rows first"),
    after: int | None = Query(None, ge=0, description="resume from a cursor (overrides `start`)"),
    wait: float = Query(0, ge=0, le=300, description="seconds to wait for streaming to begin before closing"),
    interval: float = Query(0.25, ge=0.05, le=5, description="polling interval in seconds"),
    batch: int = Query(500, ge=1, le=10_000, description="max rows sent per write"),
    last_event_id: str | None = Header(None),
) -> StreamingResponse:
    """Hold the connection open and push rows as they are generated; closes when the stream stops."""
    dataset = _dataset(name)
    if after is None and last_event_id and last_event_id.isdigit():
        after = int(last_event_id)
    cursor = after if after is not None else (0 if start == "beginning" else dataset.total)
    sse = format == "sse"
    return StreamingResponse(
        _follow(dataset.name, cursor, wait, interval, batch, sse),
        media_type="text/event-stream" if sse else "application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _follow(name: str, cursor: int, wait: float, interval: float, batch: int, sse: bool):
    started = last_write = time.monotonic()
    while True:
        dataset = STORE.get(name)
        if dataset is None:
            return
        live = dataset.streaming  # read before tailing so a final batch is never missed
        rows, new_cursor = dataset.tail(cursor, batch)
        if rows:
            first = new_cursor - len(rows)
            lines = (json.dumps(row, default=str) for row in rows)
            yield "".join(f"id: {first + i + 1}\ndata: {line}\n\n" if sse else f"{line}\n"
                          for i, line in enumerate(lines))
            cursor, last_write = new_cursor, time.monotonic()
            await asyncio.sleep(0)
            continue
        now = time.monotonic()
        if not live and now - started >= wait:
            return
        if sse and now - last_write >= 15:
            yield ": keep-alive\n\n"
            last_write = now
        await asyncio.sleep(interval)


@app.post("/datasets/{name}/generate")
def generate(name: str, rows: int = Query(100, ge=1, le=MAX_ROWS_ONCE), append: bool = False) -> dict:
    dataset = _dataset(name)
    dataset.generate(rows, replace=not append)
    return dataset.info()


@app.post("/datasets/{name}/stream/{action}")
def stream(name: str, action: str) -> dict:
    dataset = _dataset(name)
    if action == "start":
        dataset.start_stream()
    elif action == "stop":
        dataset.stop_stream()
    else:
        raise HTTPException(422, "action must be 'start' or 'stop'")
    return dataset.info()
