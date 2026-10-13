"""Runs the API inside another process (the Streamlit app) on a background thread."""

import socket
import threading
import time

import uvicorn

from .app import app

_server: uvicorn.Server | None = None
_server_lock = threading.Lock()


def _port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def start_api(host: str, port: int) -> tuple[bool, str]:
    """Start the API once per process. Returns (running, message)."""
    global _server
    with _server_lock:
        if _server is not None and _server.started:
            return True, f"http://{host}:{port}"
        if not _port_free(host, port):
            return False, f"port {port} is already in use"
        _server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
        threading.Thread(target=_server.run, name="mock-data-api", daemon=True).start()
        for _ in range(50):
            if _server.started:
                return True, f"http://{host}:{port}"
            time.sleep(0.1)
        return False, "API server failed to start"
