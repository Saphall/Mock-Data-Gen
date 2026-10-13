"""HTTP routes exposing generated datasets to other services."""

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

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
