"""Built-in dataset templates, grouped by category."""

CATEGORIES = ["People", "Commerce", "Content", "Ops & Infra", "Finance", "Other"]


def _c(name: str, type_: str, options: str = "", null_pct: float = 0.0) -> dict:
    return {"name": name, "type": type_, "options": options, "null_pct": null_pct}


def _schema(category: str, description: str, dataset: str, eps: int, *columns: dict) -> dict:
    return {"category": category, "description": description, "dataset": dataset, "eps": eps,
            "spec": {"kind": "schema", "columns": list(columns)}}


TEMPLATES: dict[str, dict] = {
    "Security Logs": {
        "category": "Ops & Infra",
        "description": "SIEM-style events with injectable attack scenarios: brute force, port scan, impossible travel, data exfil, off-hours admin.",
        "dataset": "security_logs",
        "eps": 20,
        "spec": {"kind": "generator", "generator": "security_logs", "options": {"anomalies_per_minute": 2.0}},
    },
    # ---- People
    "Users": _schema(
        "People", "Profile records for seeding user tables.", "users", 1,
        _c("id", "uuid"), _c("name", "full_name"), _c("email", "email"), _c("username", "username"),
        _c("phone", "phone", "", 10), _c("company", "company"), _c("job_title", "job_title"),
        _c("country", "country"), _c("is_active", "boolean", "0.9"), _c("signed_up", "date", "2020-01-01,now"),
    ),
    "Employees": _schema(
        "People", "HR directory with department, salary and manager.", "employees", 1,
        _c("employee_id", "sequence", "1000,1"), _c("name", "full_name"), _c("email", "email"),
        _c("department", "department"), _c("job_title", "job_title"), _c("salary", "integer", "40000,180000"),
        _c("hired_on", "date", "2015-01-01,now"), _c("manager_id", "integer", "1000,1100", 10),
        _c("is_active", "boolean", "0.95"),
    ),
    "Customers": _schema(
        "People", "CRM accounts with plan tier and signup date.", "customers", 1,
        _c("customer_id", "uuid"), _c("name", "full_name"), _c("email", "email"), _c("phone", "phone", "", 15),
        _c("company", "company"), _c("city", "city"), _c("country_code", "country_code"),
        _c("tier", "choice", "free:60|pro:30|enterprise:10"), _c("signed_up", "date", "2019-01-01,now"),
    ),
    "Addresses": _schema(
        "People", "Mailing and shipping addresses with coordinates.", "addresses", 1,
        _c("id", "uuid"), _c("street", "street_address"), _c("city", "city"), _c("state", "state"),
        _c("zip_code", "zip_code"), _c("country", "country"), _c("latitude", "latitude"),
        _c("longitude", "longitude"), _c("timezone", "timezone"),
    ),
    "Students": _schema(
        "People", "University enrolment records.", "students", 1,
        _c("student_id", "sequence", "20000,1"), _c("name", "full_name"), _c("email", "email"),
        _c("age", "age", "17,30"), _c("major", "choice", "CS|Biology|Law|Design|Economics|Physics"),
        _c("gpa", "float", "2,4,2"), _c("enrolled_on", "date", "2020-01-01,now"),
    ),
    "Sales Leads": _schema(
        "People", "Inbound leads with source, status and score.", "leads", 2,
        _c("lead_id", "uuid"), _c("name", "full_name"), _c("email", "email"), _c("company", "company"),
        _c("source", "choice", "web:40|referral:25|ads:25|event:10"),
        _c("status", "choice", "new:40|contacted:30|qualified:20|lost:10"), _c("score", "integer", "0,100"),
        _c("created_at", "datetime", "-30d,now"),
    ),
    # ---- Commerce
    "Products": _schema(
        "Commerce", "Catalog items with SKU, category, price and stock.", "products", 1,
        _c("sku", "sequence", "10000,1"), _c("name", "product_name"), _c("category", "product_category"),
        _c("price", "price", "2,1200"), _c("stock", "integer", "0,500"), _c("rating", "float", "1,5,1"),
        _c("description", "sentence", "12"),
    ),
    "E-commerce Orders": _schema(
        "Commerce", "Customer orders with status, amount and shipping city.", "orders", 2,
        _c("order_id", "sequence", "1000,1"), _c("customer_id", "uuid"), _c("customer_email", "email"),
        _c("status", "order_status"), _c("total", "price", "5,900"),
        _c("currency", "choice", "USD:70|EUR:20|GBP:10"), _c("items", "integer", "1,8"), _c("city", "city"),
        _c("created_at", "datetime", "-30d,now"),
    ),
    "Product Reviews": _schema(
        "Commerce", "Ratings and review text per product.", "reviews", 2,
        _c("review_id", "uuid"), _c("product_sku", "sku"), _c("author", "username"), _c("rating", "rating"),
        _c("title", "title"), _c("body", "paragraph", "2"), _c("helpful_votes", "integer", "0,200"),
        _c("created_at", "datetime", "-180d,now"),
    ),
    "Shopping Carts": _schema(
        "Commerce", "Open carts with subtotal and optional coupon.", "carts", 2,
        _c("cart_id", "uuid"), _c("user_id", "uuid"), _c("items", "integer", "1,12"),
        _c("subtotal", "price", "10,1500"), _c("currency", "currency_code"),
        _c("coupon", "choice", "SAVE10|FREESHIP|WELCOME5", 70), _c("updated_at", "datetime", "-7d,now"),
    ),
    "Inventory": _schema(
        "Commerce", "Warehouse stock levels with barcodes.", "inventory", 1,
        _c("sku", "sku"), _c("name", "product_name"), _c("barcode", "ean13"),
        _c("warehouse", "choice", "NYC|LON|SIN|FRA|SYD"), _c("quantity", "integer", "0,2000"),
        _c("reorder_level", "integer", "20,200"), _c("last_counted", "date", "-90d,now"),
    ),
    "Shipments": _schema(
        "Commerce", "Parcel tracking with carrier, route and delivery time.", "shipments", 2,
        _c("tracking_id", "uuid"), _c("carrier", "choice", "DHL|FedEx|UPS|USPS"),
        _c("status", "choice", "in_transit:50|delivered:35|delayed:10|returned:5"), _c("origin", "city"),
        _c("destination", "city"), _c("weight_kg", "float", "0.1,40,1"), _c("shipped_at", "datetime", "-14d,now"),
        _c("delivered_at", "datetime", "-7d,now", 35),
    ),
    # ---- Content
    "Blog Posts": _schema(
        "Content", "CMS blog entries with author and tags.", "blog_posts", 1,
        _c("id", "uuid"), _c("title", "title"), _c("slug", "slug"), _c("author", "full_name"),
        _c("category", "choice", "tech|design|product|culture|news"), _c("body", "paragraph", "5"),
        _c("views", "lognormal_int", "6,1"), _c("published_at", "datetime", "-365d,now"),
    ),
    "Comments": _schema(
        "Content", "User comments and reviews on posts.", "comments", 3,
        _c("commentId", "uuid"), _c("postId", "uuid"), _c("author", "username"), _c("body", "sentence", "14"),
        _c("likes", "integer", "0,500"), _c("createdAt", "datetime", "-30d,now"),
    ),
    "Chat Messages": _schema(
        "Content", "Real-time messaging app data.", "chat_messages", 5,
        _c("messageId", "uuid"), _c("channelId", "choice", "general|random|eng|support|design"),
        _c("sender", "username"), _c("text", "sentence", "10"), _c("read", "boolean", "0.8"),
        _c("sentAt", "now"),
    ),
    "Social Posts": _schema(
        "Content", "Short posts with hashtags and engagement counts.", "social_posts", 3,
        _c("post_id", "uuid"), _c("handle", "username"), _c("text", "sentence", "16"), _c("hashtag", "hashtag"),
        _c("likes", "lognormal_int", "4,1.2"), _c("reposts", "lognormal_int", "2,1"), _c("posted_at", "now"),
    ),
    "Notifications": _schema(
        "Content", "In-app notifications with read state.", "notifications", 3,
        _c("id", "uuid"), _c("user_id", "uuid"), _c("type", "choice", "mention|follow|comment|system|billing"),
        _c("title", "title"), _c("read", "boolean", "0.6"), _c("created_at", "datetime", "-14d,now"),
    ),
    "Support Tickets": _schema(
        "Content", "Helpdesk tickets with priority and assignee.", "tickets", 1,
        _c("ticket_id", "sequence", "5000,1"), _c("requester", "email"), _c("subject", "title"),
        _c("priority", "choice", "low:40|normal:35|high:20|urgent:5"),
        _c("status", "choice", "open:35|pending:20|solved:45"), _c("assignee", "full_name", "", 20),
        _c("created_at", "datetime", "-30d,now"),
    ),
    # ---- Ops & Infra
    "Log Analytics Starter Kit": _schema(
        "Ops & Infra", "Application request logs: level, service, route, status, latency, client.", "app_logs", 10,
        _c("timestamp", "now"), _c("level", "log_level"), _c("service", "choice", "api|web|worker|billing|auth"),
        _c("method", "http_method"),
        _c("path", "choice", "/api/orders|/api/users|/api/search|/login|/health|/static/app.js"),
        _c("status", "http_status"), _c("latency_ms", "lognormal_int", "4,0.8"), _c("client_ip", "ipv4"),
        _c("user_agent", "user_agent"), _c("request_id", "uuid"),
    ),
    "API Logs": _schema(
        "Ops & Infra", "HTTP request logs with response codes.", "api_logs", 10,
        _c("requestId", "uuid"), _c("method", "http_method"), _c("path", "uri_path"), _c("status", "http_status"),
        _c("latencyMs", "lognormal_int", "4,0.8"), _c("ip", "ipv4"), _c("userAgent", "user_agent"),
        _c("timestamp", "now"),
    ),
    "Web Analytics Starter Kit": _schema(
        "Ops & Infra", "Page view events with session, device, referrer and geography.", "web_events", 5,
        _c("timestamp", "now"), _c("session_id", "uuid"), _c("user_id", "integer", "1,5000", 15),
        _c("event", "choice", "pageview:80|click:15|signup:3|purchase:2"),
        _c("pathname", "choice", "/|/pricing|/docs|/blog|/signup|/checkout"),
        _c("referrer", "choice", "google.com|twitter.com|news.ycombinator.com|direct", 5),
        _c("device", "choice", "desktop:55|mobile:40|tablet:5"), _c("country", "country_code"),
    ),
    "Server Metrics": _schema(
        "Ops & Infra", "Host CPU, memory and disk usage samples.", "server_metrics", 5,
        _c("ts", "now"), _c("host", "choice", "web-01|web-02|db-01|cache-01|worker-01"),
        _c("cpu_pct", "float", "1,100,1"), _c("mem_pct", "float", "10,95,1"), _c("disk_pct", "float", "20,90,1"),
        _c("net_in_kbps", "lognormal_int", "7,1"), _c("net_out_kbps", "lognormal_int", "7,1"),
    ),
    "Error Logs": _schema(
        "Ops & Infra", "Application errors with trace ids.", "error_logs", 3,
        _c("timestamp", "now"), _c("service", "choice", "api|web|worker|billing|auth"),
        _c("level", "choice", "ERROR:80|CRITICAL:20"), _c("message", "sentence", "9"), _c("trace_id", "md5"),
        _c("version", "semver"), _c("host", "domain"),
    ),
    "Deployments": _schema(
        "Ops & Infra", "CI/CD deploy history by service and environment.", "deployments", 1,
        _c("deployment_id", "uuid"), _c("service", "choice", "api|web|worker|billing|auth"),
        _c("version", "semver"), _c("environment", "choice", "prod:30|staging:40|dev:30"),
        _c("status", "choice", "succeeded:85|failed:10|rolled_back:5"), _c("deployed_by", "username"),
        _c("commit", "sha256"), _c("deployed_at", "datetime", "-30d,now"),
    ),
    "IoT Sensors": _schema(
        "Ops & Infra", "Telemetry from devices: temperature, humidity, battery, location.", "iot_readings", 10,
        _c("ts", "now"),
        _c("device_id", "choice", "sensor-01|sensor-02|sensor-03|sensor-04|sensor-05|sensor-06"),
        _c("temperature_c", "float", "15,35,2"), _c("humidity_pct", "float", "20,80,1"),
        _c("battery_pct", "integer", "5,100"), _c("lat", "latitude"), _c("lon", "longitude"),
    ),
    "Audit Logs": _schema(
        "Ops & Infra", "Who did what to which resource, and from where.", "audit_logs", 2,
        _c("event_id", "uuid"), _c("actor", "email"),
        _c("action", "choice", "login|logout|create|update|delete|export"),
        _c("resource", "choice", "user|invoice|project|api_key|report"), _c("ip", "ipv4"),
        _c("success", "boolean", "0.95"), _c("timestamp", "now"),
    ),
    # ---- Finance
    "Invoices": _schema(
        "Finance", "Billing invoices with due dates and payment state.", "invoices", 1,
        _c("invoice_no", "sequence", "5000,1"), _c("company", "company"), _c("amount", "price", "50,25000"),
        _c("currency", "currency_code"), _c("issued", "date", "-90d,now"), _c("due", "date", "now,+30d"),
        _c("status", "choice", "paid:60|open:25|overdue:15"),
    ),
    "Transactions": _schema(
        "Finance", "Card and account transactions.", "transactions", 5,
        _c("txn_id", "uuid"), _c("account", "bban"), _c("amount", "price", "1,5000"), _c("currency", "currency_code"),
        _c("type", "choice", "credit:45|debit:55"), _c("merchant", "company"), _c("card", "credit_card_type"),
        _c("status", "choice", "settled:90|pending:7|failed:3"), _c("timestamp", "now"),
    ),
    "Bank Accounts": _schema(
        "Finance", "Account holders with IBAN and balance.", "bank_accounts", 1,
        _c("account_id", "uuid"), _c("holder", "full_name"), _c("iban", "iban"),
        _c("balance", "price", "0,250000"), _c("currency", "currency_code"), _c("opened_on", "date", "2005-01-01,now"),
        _c("status", "choice", "active:90|frozen:3|closed:7"),
    ),
    "Crypto Wallets": _schema(
        "Finance", "Blockchain wallet addresses and balances.", "crypto_wallets", 2,
        _c("address", "ethereum_address"), _c("balance", "float", "0,50,6"),
        _c("chain", "choice", "ethereum:50|bitcoin:30|polygon:20"), _c("tx_count", "lognormal_int", "3,1.2"),
        _c("last_active", "datetime", "-90d,now"),
    ),
    "Stock Prices": _schema(
        "Finance", "Ticker quotes with price and volume.", "stock_ticks", 5,
        _c("ts", "now"), _c("symbol", "choice", "AAPL|MSFT|GOOG|AMZN|TSLA|NVDA"), _c("price", "float", "50,500,2"),
        _c("volume", "lognormal_int", "6,1"),
    ),
    "Subscriptions": _schema(
        "Finance", "SaaS subscriptions with plan, MRR and renewal date.", "subscriptions", 1,
        _c("subscription_id", "uuid"), _c("customer", "email"), _c("plan", "choice", "starter:50|pro:35|team:15"),
        _c("status", "choice", "active:75|trialing:10|past_due:5|canceled:10"), _c("mrr", "price", "9,499"),
        _c("started_on", "date", "2021-01-01,now"), _c("renews_on", "date", "now,+365d"),
    ),
    # ---- Other
    "Events": _schema(
        "Other", "Conferences and meetups with venue and ticket price.", "events", 1,
        _c("event_id", "uuid"), _c("title", "title"), _c("city", "city"), _c("country", "country_code"),
        _c("starts_at", "datetime", "now,+180d"), _c("capacity", "integer", "20,5000"),
        _c("ticket_price", "price", "0,500"),
    ),
    "Flights": _schema(
        "Other", "Scheduled flights with route, duration and fare.", "flights", 2,
        _c("flight_no", "choice", "AA101|BA202|LH303|EK404|SQ505|DL606"), _c("origin", "city"),
        _c("destination", "city"), _c("departure", "datetime", "now,+30d"), _c("duration_min", "integer", "60,720"),
        _c("fare", "price", "80,2400"), _c("status", "choice", "on_time:80|delayed:15|cancelled:5"),
    ),
    "Vehicles": _schema(
        "Other", "Fleet or listing data with make, model and mileage.", "vehicles", 1,
        _c("vehicle_id", "uuid"), _c("make", "choice", "Toyota|Ford|BMW|Tesla|Honda|Kia"), _c("model", "word"),
        _c("year", "integer", "2005,2025"), _c("mileage_km", "lognormal_int", "10,0.8"), _c("color", "color_name"),
        _c("price", "price", "2000,90000"),
    ),
    "Real Estate Listings": _schema(
        "Other", "Property listings with size, rooms and asking price.", "listings", 1,
        _c("listing_id", "uuid"), _c("address", "address"), _c("city", "city"), _c("price", "price", "80000,2500000"),
        _c("bedrooms", "integer", "1,6"), _c("bathrooms", "integer", "1,4"), _c("sqft", "integer", "400,6000"),
        _c("listed_on", "date", "-120d,now"),
    ),
    "Courses": _schema(
        "Other", "Online course catalog with rating and enrolment.", "courses", 1,
        _c("course_id", "uuid"), _c("title", "title"), _c("instructor", "full_name"),
        _c("level", "choice", "beginner:45|intermediate:35|advanced:20"), _c("hours", "integer", "1,60"),
        _c("rating", "float", "3,5,1"), _c("enrolled", "lognormal_int", "6,1.2"),
    ),
}

DEFAULT_TEMPLATE = "Security Logs"
