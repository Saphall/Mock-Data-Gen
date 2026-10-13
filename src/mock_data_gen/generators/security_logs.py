"""Realistic mock security logs: steady normal traffic plus injectable attack scenarios."""

import random
import uuid
from datetime import datetime, timedelta, timezone

SCENARIOS = ("brute_force", "port_scan", "impossible_travel", "data_exfil", "off_hours_admin")

DEFAULT_CONFIG = {
    "events_per_second": 20,
    "anomalies_per_minute": 2.0,
    "scenarios": list(SCENARIOS),
}

COUNTRIES = ["US", "DE", "GB", "IN", "BR", "JP", "AU", "CA", "FR", "SG"]
SERVERS = {
    "web-01": "10.0.10.11",
    "web-02": "10.0.10.12",
    "db-01": "10.0.20.5",
    "auth-01": "10.0.30.5",
    "vpn-01": "10.0.30.6",
    "files-01": "10.0.40.5",
}
DNS_RESOLVER = "10.0.0.2"
_NAMES = [
    "alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi", "ivan", "judy",
    "ken", "laura", "mallory", "nina", "oscar", "peggy", "quentin", "rita", "sam", "trudy",
    "uma", "victor", "wendy", "xavier", "yara", "zane", "amir", "bianca", "chen", "dina",
]
USERS = [
    {
        "name": name,
        "country": "US" if i % 5 else COUNTRIES[i // 5 % len(COUNTRIES)],
        "host": f"ws-{i + 1:03d}",
        "ip": f"10.0.1.{i + 10}",
    }
    for i, name in enumerate(_NAMES)
]
PATHS = ["/", "/login", "/api/orders", "/api/users", "/static/app.js", "/dashboard", "/api/search", "/health"]
DOMAINS = ["github.com", "slack.com", "office365.com", "google.com", "s3.amazonaws.com", "zoom.us", "npmjs.org"]
PROCESSES = ["chrome.exe", "python3", "code", "outlook.exe", "ssh", "docker", "node"]

# (event type, weight)
NORMAL_MIX = [
    ("web_request", 40),
    ("dns_query", 20),
    ("file_access", 12),
    ("login_success", 10),
    ("file_transfer", 6),
    ("logout", 6),
    ("process_start", 4),
    ("login_failed", 2),
]

COLUMNS = [
    "event_id", "timestamp", "host", "source_ip", "dest_ip", "dest_port", "username",
    "event_type", "severity", "country", "bytes_out", "message",
]


def _ts(ts: datetime) -> str:
    return f"{ts:%Y-%m-%d %H:%M:%S}.{ts.microsecond // 1000:03d}"


def _public_ip() -> str:
    first = random.choice([45, 91, 103, 141, 185, 194, 203])
    return f"{first}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _event(ts, host, source_ip, dest_ip, dest_port, username, event_type, severity, country,
           bytes_out, message) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": _ts(ts),
        "host": host,
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "username": username,
        "event_type": event_type,
        "severity": severity,
        "country": country,
        "bytes_out": bytes_out,
        "message": message,
    }


def normal_event(now: datetime) -> dict:
    ts = now - timedelta(milliseconds=random.randint(0, 999))
    user = random.choice(USERS)
    name, ip, country = user["name"], user["ip"], user["country"]
    kind = random.choices([k for k, _ in NORMAL_MIX], [w for _, w in NORMAL_MIX])[0]

    if kind == "web_request":
        host = random.choice(["web-01", "web-02"])
        status = random.choices([200, 301, 404, 500], [85, 6, 7, 2])[0]
        path = random.choice(PATHS)
        return _event(ts, host, ip, SERVERS[host], 443, name, kind, "INFO" if status < 400 else "WARNING",
                      country, random.randint(200, 50_000), f'"GET {path} HTTP/1.1" {status}')
    if kind == "dns_query":
        domain = random.choice(DOMAINS)
        return _event(ts, user["host"], ip, DNS_RESOLVER, 53, name, kind, "INFO", country, 0,
                      f"DNS query for {domain}")
    if kind == "file_access":
        return _event(ts, "files-01", ip, SERVERS["files-01"], 445, name, kind, "INFO", country, 0,
                      f"Opened \\\\files-01\\shared\\{random.choice(['reports', 'hr', 'eng', 'finance'])}\\doc{random.randint(1, 500)}.docx")
    if kind == "login_success":
        host = random.choice(["auth-01", "vpn-01"])
        return _event(ts, host, ip, SERVERS[host], random.choice([22, 443, 3389]), name, kind, "INFO", country, 0,
                      f"Accepted login for {name} from {ip}")
    if kind == "file_transfer":
        size = int(min(random.lognormvariate(11, 1.2), 5_000_000))
        return _event(ts, user["host"], ip, _public_ip(), 443, name, kind, "INFO", country, size,
                      f"Outbound transfer of {size // 1024} KB")
    if kind == "logout":
        return _event(ts, "auth-01", ip, SERVERS["auth-01"], 443, name, kind, "INFO", country, 0,
                      f"Session closed for {name}")
    if kind == "process_start":
        return _event(ts, user["host"], ip, ip, 0, name, kind, "INFO", country, 0,
                      f"Process started: {random.choice(PROCESSES)}")
    return _event(ts, "auth-01", ip, SERVERS["auth-01"], 22, name, "login_failed", "WARNING", country, 0,
                  f"Failed password for {name} from {ip} port {random.randint(1024, 65535)} ssh2")


def _brute_force(now: datetime) -> list[dict]:
    attacker, country = _public_ip(), random.choice(COUNTRIES[1:])
    target = random.choice(["root", "admin", random.choice(USERS)["name"]])
    auth = SERVERS["auth-01"]
    events = [
        _event(now - timedelta(seconds=random.uniform(0, 20)), "auth-01", attacker, auth, 22, target,
               "login_failed", "WARNING", country, 0,
               f"Failed password for {target} from {attacker} port {random.randint(1024, 65535)} ssh2")
        for _ in range(random.randint(25, 80))
    ]
    if random.random() < 0.4:
        events.append(_event(now, "auth-01", attacker, auth, 22, target, "login_success", "CRITICAL", country, 0,
                             f"Accepted password for {target} from {attacker} after repeated failures"))
    return events


def _port_scan(now: datetime) -> list[dict]:
    attacker, country = _public_ip(), random.choice(COUNTRIES[1:])
    host = random.choice(list(SERVERS))
    target = SERVERS[host]
    ports = random.sample(range(1, 10_000), random.randint(40, 200))
    events = [
        _event(now - timedelta(seconds=random.uniform(0, 10)), host, attacker, target, port, "-",
               "firewall_deny", "WARNING", country, 0, f"DROP TCP {attacker} -> {target}:{port}")
        for port in ports
    ]
    events.append(_event(now, host, attacker, target, 0, "-", "port_scan", "ERROR", country, 0,
                         f"Port scan detected from {attacker}"))
    return events


def _impossible_travel(now: datetime) -> list[dict]:
    user = random.choice(USERS)
    far = random.choice([c for c in COUNTRIES if c != user["country"]])
    remote_ip = _public_ip()
    vpn = SERVERS["vpn-01"]
    return [
        _event(now - timedelta(minutes=2), "vpn-01", user["ip"], vpn, 443, user["name"], "login_success", "INFO",
               user["country"], 0, f"VPN login for {user['name']} from {user['country']}"),
        _event(now, "vpn-01", remote_ip, vpn, 443, user["name"], "login_success", "ERROR", far, 0,
               f"VPN login for {user['name']} from {far} two minutes after {user['country']}"),
    ]


def _data_exfil(now: datetime) -> list[dict]:
    user = random.choice(USERS)
    destination = _public_ip()
    events = []
    for _ in range(random.randint(2, 5)):
        size = random.randint(300_000_000, 3_000_000_000)
        events.append(_event(now - timedelta(seconds=random.uniform(0, 30)), user["host"], user["ip"], destination,
                             443, user["name"], "file_transfer", "ERROR", user["country"], size,
                             f"Large outbound transfer of {size // 1_000_000} MB to {destination}"))
    return events


def _off_hours_admin(now: datetime) -> list[dict]:
    # Event time is the most recent 02:00-04:30 UTC; the ingested_at column still reflects "now".
    ts = now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(minutes=random.randint(0, 150))
    if ts > now:
        ts -= timedelta(days=1)
    admin = random.choice(["root", "admin"])
    ip, country = _public_ip(), random.choice(COUNTRIES[1:])
    return [
        _event(ts, "vpn-01", ip, SERVERS["vpn-01"], 443, admin, "login_success", "ERROR", country, 0,
               f"{admin} logged in from {ip} outside business hours"),
        _event(ts + timedelta(seconds=40), "auth-01", ip, SERVERS["auth-01"], 22, admin, "privilege_escalation",
               "CRITICAL", country, 0, f"sudo session opened for {admin}"),
        _event(ts + timedelta(minutes=2), "db-01", ip, SERVERS["db-01"], 5432, admin, "file_access", "ERROR",
               country, 0, "Database dump of customers table"),
    ]


_BUILDERS = {
    "brute_force": _brute_force,
    "port_scan": _port_scan,
    "impossible_travel": _impossible_travel,
    "data_exfil": _data_exfil,
    "off_hours_admin": _off_hours_admin,
}


def inject(scenario: str, now: datetime | None = None) -> list[dict]:
    if scenario not in _BUILDERS:
        raise ValueError(f"unknown scenario: {scenario}")
    return _BUILDERS[scenario](now or datetime.now(timezone.utc))


def normalize_config(raw: dict) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    for key, lo, hi, cast in (("events_per_second", 1, 5000, int), ("anomalies_per_minute", 0, 600, float)):
        try:
            cfg[key] = min(max(cast(raw.get(key, cfg[key])), lo), hi)
        except (TypeError, ValueError):
            pass
    scenarios = raw.get("scenarios")
    if isinstance(scenarios, list):
        cfg["scenarios"] = [s for s in SCENARIOS if s in scenarios]
    return cfg


def generate_batch(config: dict, now: datetime | None = None) -> list[dict]:
    """One second of traffic: normal events plus, on average, anomalies_per_minute/60 attack bursts."""
    now = now or datetime.now(timezone.utc)
    events = [normal_event(now) for _ in range(config["events_per_second"])]
    rate = config["anomalies_per_minute"] / 60
    bursts = int(rate) + (1 if random.random() < rate - int(rate) else 0)
    if config["scenarios"]:
        for _ in range(bursts):
            events.extend(inject(random.choice(config["scenarios"]), now))
    return events
