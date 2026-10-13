"""Built-in generators for domain-specific data that a column schema cannot express."""

from datetime import datetime

from . import security_logs


class SecurityLogGenerator:
    tick_based = True
    column_names = security_logs.COLUMNS

    def __init__(self, options: dict):
        self._options = options

    def batch(self, n: int, now: datetime) -> list[dict]:
        cfg = security_logs.normalize_config({**self._options, "events_per_second": n})
        return security_logs.generate_batch(cfg, now)


GENERATORS = {
    "security_logs": {
        "label": "Security logs",
        "defaults": {
            "anomalies_per_minute": security_logs.DEFAULT_CONFIG["anomalies_per_minute"],
            "scenarios": list(security_logs.SCENARIOS),
        },
        "columns": security_logs.COLUMNS,
        "scenarios": security_logs.SCENARIOS,
        "factory": SecurityLogGenerator,
    },
}
