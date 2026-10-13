"""Column type registry: each type builds a callable that produces one value per row."""

import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

from faker import Faker

fake = Faker()

Producer = Callable[[datetime], Any]
Factory = Callable[[str], Producer]


@dataclass(frozen=True)
class FieldType:
    key: str
    group: str
    desc: str
    factory: Factory
    hint: str = ""
    label: str = ""

    @property
    def title(self) -> str:
        return self.label or self.key.replace("_", " ").title()


def _parts(options: str, sep: str = ",") -> list[str]:
    return [p.strip() for p in options.split(sep) if p.strip()]


def _num(text: str, default: float) -> float:
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


_REL_TIME = re.compile(r"^([+-]?\d+)([smhdw])$")
_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def _parse_time(text: str, now: datetime) -> datetime:
    text = text.strip().lower()
    if text in ("", "now"):
        return now
    if m := _REL_TIME.match(text):
        return now + timedelta(seconds=int(m.group(1)) * _UNITS[m.group(2)])
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return now
    return parsed.replace(tzinfo=now.tzinfo) if parsed.tzinfo is None else parsed


def _fmt_dt(value: datetime) -> str:
    return f"{value:%Y-%m-%d %H:%M:%S}.{value.microsecond // 1000:03d}"


def _simple(fn: Callable[[], Any]) -> Factory:
    return lambda _options: (lambda _now: fn())


def _pick(values: list, weights: list[float] | None = None) -> Factory:
    return lambda _options: (lambda _now: random.choices(values, weights)[0])


def _integer(options: str) -> Producer:
    p = _parts(options)
    lo, hi = int(_num(p[0], 0)) if p else 0, int(_num(p[1], 1000)) if len(p) > 1 else 1000
    return lambda _now: random.randint(min(lo, hi), max(lo, hi))


def _age(options: str) -> Producer:
    return _integer(options or "18,90")


def _float(options: str) -> Producer:
    p = _parts(options)
    lo, hi = _num(p[0], 0) if p else 0.0, _num(p[1], 1000) if len(p) > 1 else 1000.0
    places = int(_num(p[2], 2)) if len(p) > 2 else 2
    return lambda _now: round(random.uniform(min(lo, hi), max(lo, hi)), places)


def _percentage(_options: str) -> Producer:
    return lambda _now: round(random.uniform(0, 100), 1)


def _boolean(options: str) -> Producer:
    p = _num(options, 0.5)
    return lambda _now: random.random() < p


def _sequence(options: str) -> Producer:
    p = _parts(options)
    state = {"next": int(_num(p[0], 1)) if p else 1}
    step = int(_num(p[1], 1)) if len(p) > 1 else 1

    def produce(_now: datetime) -> int:
        value = state["next"]
        state["next"] += step
        return value

    return produce


def _choice(options: str) -> Producer:
    items = _parts(options, "|") or ["a", "b", "c"]
    values, weights = [], []
    for item in items:
        value, _, weight = item.rpartition(":") if re.search(r":\d+(\.\d+)?$", item) else (item, "", "1")
        values.append(value)
        weights.append(_num(weight, 1))
    return lambda _now: random.choices(values, weights)[0]


def _datetime(options: str) -> Producer:
    p = _parts(options)
    start, end = (p[0] if p else "-30d"), (p[1] if len(p) > 1 else "now")

    def produce(now: datetime) -> str:
        a, b = _parse_time(start, now), _parse_time(end, now)
        a, b = min(a, b), max(a, b)
        return _fmt_dt(a + (b - a) * random.random())

    return produce


def _date(options: str) -> Producer:
    produce = _datetime(options)
    return lambda now: produce(now)[:10]


def _time_of_day(_options: str) -> Producer:
    return lambda _now: fake.time()


def _unix_ts(options: str) -> Producer:
    produce = _datetime(options)
    return lambda now: int(datetime.fromisoformat(produce(now)).timestamp())


def _now(_options: str) -> Producer:
    return lambda now: _fmt_dt(now - timedelta(milliseconds=random.randint(0, 999)))


def _text(fn_name: str) -> Factory:
    def factory(options: str) -> Producer:
        count = int(_num(options, 0)) or None
        if fn_name == "sentence":
            return lambda _now: fake.sentence(nb_words=count or 8)
        if fn_name == "paragraph":
            return lambda _now: fake.paragraph(nb_sentences=count or 3)
        return lambda _now: " ".join(fake.words(nb=count or 1))

    return factory


def _static(options: str) -> Producer:
    return lambda _now: options


def _price(options: str) -> Producer:
    p = _parts(options)
    lo, hi = _num(p[0], 1) if p else 1.0, _num(p[1], 500) if len(p) > 1 else 500.0
    return lambda _now: round(random.uniform(lo, hi), 2)


def _http_status(_options: str) -> Producer:
    return lambda _now: random.choices([200, 201, 204, 301, 400, 401, 403, 404, 500, 503],
                                       [70, 5, 3, 4, 4, 2, 2, 6, 3, 1])[0]


def _lognormal(options: str) -> Producer:
    p = _parts(options)
    mu, sigma = _num(p[0], 5) if p else 5.0, _num(p[1], 1) if len(p) > 1 else 1.0
    return lambda _now: int(random.lognormvariate(mu, sigma))


_PRODUCT_NOUNS = ["Chair", "Lamp", "Backpack", "Headphones", "Keyboard", "Bottle", "Watch", "Jacket", "Mug", "Speaker"]
_BECH32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _t(key: str, group: str, desc: str, factory: Factory, hint: str = "", label: str = "") -> tuple[str, FieldType]:
    return key, FieldType(key, group, desc, factory, hint, label)


FIELD_TYPES: dict[str, FieldType] = dict([
    # Person
    _t("full_name", "Person", "A first and last name.", _simple(fake.name)),
    _t("first_name", "Person", "Given name.", _simple(fake.first_name)),
    _t("last_name", "Person", "Family name.", _simple(fake.last_name)),
    _t("email", "Person", "Email address on an example domain.", _simple(fake.email)),
    _t("username", "Person", "Short login handle.", _simple(fake.user_name)),
    _t("phone", "Person", "Phone number.", _simple(fake.phone_number), label="Phone Number"),
    _t("avatar_url", "Person", "Profile picture URL.",
       _simple(lambda: f"https://i.pravatar.cc/150?img={random.randint(1, 70)}"), label="Avatar URL"),
    _t("gender", "Person", "Gender label.", _pick(["Female", "Male", "Non-binary"], [48, 48, 4])),
    _t("job_title", "Person", "Occupation.", _simple(fake.job)),
    _t("company", "Person", "Company name.", _simple(fake.company)),
    _t("bio", "Person", "Short profile blurb.", _simple(lambda: fake.text(max_nb_chars=140)), label="Bio / About"),
    _t("password", "Person", "Random password string, for fixtures only.", _simple(lambda: fake.password(length=14))),
    _t("age", "Person", "Age in years.", _age, "min,max (default 18,90)"),
    # Location
    _t("address", "Location", "Full single-line postal address.",
       _simple(lambda: fake.address().replace("\n", ", "))),
    _t("street_address", "Location", "Street and number.", _simple(fake.street_address)),
    _t("city", "Location", "City name.", _simple(fake.city)),
    _t("state", "Location", "State or region.", _simple(fake.state), label="State / Region"),
    _t("country", "Location", "Country name.", _simple(fake.country)),
    _t("country_code", "Location", "Two-letter ISO country code.", _simple(fake.country_code)),
    _t("zip_code", "Location", "Postal code.", _simple(fake.postcode), label="Zip / Postal Code"),
    _t("latitude", "Location", "Latitude in decimal degrees.", _simple(lambda: float(fake.latitude()))),
    _t("longitude", "Location", "Longitude in decimal degrees.", _simple(lambda: float(fake.longitude()))),
    _t("timezone", "Location", "IANA time zone name.", _simple(fake.timezone)),
    # Finance
    _t("price", "Finance", "Money amount with two decimals.", _price, "min,max (e.g. 5,500)"),
    _t("currency_code", "Finance", "Three-letter currency code.", _simple(fake.currency_code)),
    _t("currency_name", "Finance", "Currency name.", _simple(fake.currency_name)),
    _t("iban", "Finance", "International bank account number.", _simple(fake.iban), label="IBAN"),
    _t("bban", "Finance", "Basic bank account number.", _simple(fake.bban), label="Account Number"),
    _t("credit_card_number", "Finance", "Card number that passes the checksum but is not real.",
       _simple(fake.credit_card_number)),
    _t("credit_card_type", "Finance", "Card network name.", _simple(fake.credit_card_provider)),
    _t("bitcoin_address", "Finance", "Bitcoin-style bech32 address.",
       _simple(lambda: "bc1q" + "".join(random.choices(_BECH32, k=38)))),
    _t("ethereum_address", "Finance", "Ethereum-style 0x address.",
       _simple(lambda: "0x" + (uuid.uuid4().hex + uuid.uuid4().hex)[:40])),
    # Internet
    _t("ipv4", "Internet", "IPv4 address.", _simple(fake.ipv4), label="IPv4 Address"),
    _t("ipv6", "Internet", "IPv6 address.", _simple(fake.ipv6), label="IPv6 Address"),
    _t("mac_address", "Internet", "Hardware address.", _simple(fake.mac_address), label="MAC Address"),
    _t("url", "Internet", "Full URL.", _simple(fake.url), label="URL"),
    _t("domain", "Internet", "Domain name.", _simple(fake.domain_name)),
    _t("slug", "Internet", "URL-safe slug.", _simple(fake.slug)),
    _t("uri_path", "Internet", "URL path.", _simple(lambda: "/" + fake.uri_path()), label="URL Path"),
    _t("image_url", "Internet", "Placeholder image URL.", _simple(fake.image_url), label="Image URL"),
    _t("user_agent", "Internet", "Browser user agent string.", _simple(fake.user_agent)),
    _t("http_method", "Internet", "HTTP verb, mostly GET.", _pick(["GET", "POST", "PUT", "DELETE", "PATCH"],
                                                                [70, 18, 5, 4, 3]), label="HTTP Method"),
    _t("http_status", "Internet", "HTTP status code, mostly 2xx.", _http_status, label="HTTP Status"),
    # Commerce
    _t("product_name", "Commerce", "Short product title.",
       _simple(lambda: f"{fake.word().title()} {random.choice(_PRODUCT_NOUNS)}")),
    _t("product_category", "Commerce", "Catalog category.",
       _pick(["electronics", "home", "garden", "toys", "books", "apparel", "sports"])),
    _t("sku", "Commerce", "Stock keeping unit code.", _simple(lambda: f"SKU-{random.randint(10000, 99999)}"),
       label="SKU"),
    _t("ean13", "Commerce", "EAN-13 barcode.", _simple(fake.ean13), label="Barcode (EAN-13)"),
    _t("color_name", "Commerce", "Color name.", _simple(fake.color_name)),
    _t("color_hex", "Commerce", "Hex color code.", _simple(fake.hex_color), label="Color Hex"),
    _t("order_status", "Commerce", "Order lifecycle state.",
       _pick(["paid", "shipped", "pending", "refunded", "cancelled"], [55, 20, 15, 5, 5])),
    _t("rating", "Commerce", "Star rating from 1 to 5.", _pick([1, 2, 3, 4, 5], [4, 6, 15, 35, 40])),
    _t("department", "Commerce", "Company department.",
       _pick(["Engineering", "Sales", "Marketing", "Support", "Finance", "HR", "Operations"])),
    # Date & Time
    _t("datetime", "Date & Time", "Random timestamp in a range.", _datetime,
       "start,end - ISO date, 'now', or -30d / -12h (e.g. -7d,now)", label="Date-Time"),
    _t("date", "Date & Time", "Random calendar date in a range.", _date, "start,end (e.g. 2023-01-01,now)"),
    _t("time", "Date & Time", "Time of day.", _time_of_day),
    _t("unix_ts", "Date & Time", "Unix timestamp in seconds.", _unix_ts, "start,end (e.g. -1d,now)",
       label="Unix Timestamp"),
    _t("now", "Date & Time", "The moment of generation, with millisecond jitter.", _now, "current time at generation",
       label="Now"),
    # Numbers
    _t("integer", "Numbers", "Whole number in a range.", _integer, "min,max (e.g. 1,100)"),
    _t("float", "Numbers", "Decimal number in a range.", _float, "min,max,decimals (e.g. 0,1,3)"),
    _t("percentage", "Numbers", "Value from 0 to 100.", _percentage),
    _t("lognormal_int", "Numbers", "Skewed integer, good for latency or size.", _lognormal, "mu,sigma (e.g. 5,1)",
       label="Log-normal Integer"),
    # Text
    _t("word", "Text", "Random word(s).", _text("word"), "word count (default 1)"),
    _t("sentence", "Text", "Random sentence.", _text("sentence"), "word count (default 8)"),
    _t("paragraph", "Text", "Random paragraph.", _text("paragraph"), "sentence count (default 3)"),
    _t("title", "Text", "Short title-cased headline.",
       _simple(lambda: fake.sentence(nb_words=5).rstrip(".").title())),
    _t("hashtag", "Text", "Hashtag.", _simple(lambda: "#" + fake.word())),
    _t("language_code", "Text", "Two-letter language code.", _simple(fake.language_code)),
    # Tech
    _t("uuid", "Tech", "Random UUID v4.", lambda _o: (lambda _n: str(uuid.uuid4())), label="UUID v4"),
    _t("md5", "Tech", "MD5 hex digest.", _simple(fake.md5), label="MD5 Hash"),
    _t("sha256", "Tech", "SHA-256 hex digest.", _simple(fake.sha256), label="SHA-256 Hash"),
    _t("file_name", "Tech", "File name with extension.", _simple(fake.file_name)),
    _t("file_extension", "Tech", "File extension.", _simple(fake.file_extension)),
    _t("mime_type", "Tech", "MIME type.", _simple(fake.mime_type), label="MIME Type"),
    _t("semver", "Tech", "Semantic version.",
       _simple(lambda: f"{random.randint(0, 9)}.{random.randint(0, 20)}.{random.randint(0, 50)}"), label="Semver"),
    _t("log_level", "Tech", "Log severity, mostly INFO.", _pick(["INFO", "DEBUG", "WARN", "ERROR"],
                                                                [70, 15, 10, 5])),
    _t("locale", "Tech", "Locale code such as en_US.", _simple(fake.locale)),
    # Custom
    _t("sequence", "Custom", "Auto-incrementing integer.", _sequence, "start,step (e.g. 1,1)"),
    _t("boolean", "Custom", "True or false.", _boolean, "probability of true, 0-1 (e.g. 0.5)"),
    _t("choice", "Custom", "Pick from your own list, optionally weighted.", _choice, "a|b|c or weighted a:70|b:30"),
    _t("static", "Custom", "The same value in every row.", _static, "constant value"),
])

GROUPS: dict[str, list[FieldType]] = {}
for _ft in FIELD_TYPES.values():
    GROUPS.setdefault(_ft.group, []).append(_ft)


def build_producer(type_key: str, options: str, null_pct: float = 0.0) -> Producer:
    if type_key not in FIELD_TYPES:
        raise ValueError(f"unknown column type: {type_key}")
    produce = FIELD_TYPES[type_key].factory((options or "").strip())
    if null_pct <= 0:
        return produce
    chance = min(null_pct, 100.0) / 100
    return lambda now: None if random.random() < chance else produce(now)
