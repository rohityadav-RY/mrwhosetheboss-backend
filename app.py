import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "submissions.json"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

# Set this to your GitHub Pages origin in production, for example:
# ALLOWED_ORIGIN=https://yourusername.github.io
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
MAX_BODY_SIZE = 10_000
ALLOWED_CATEGORIES = {
    "Smartphones", "AI", "Computers", "Cameras",
    "Gaming", "Future Technology", "Other"
}


def load_submissions():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_submissions(data):
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_file.replace(DATA_FILE)


def json_bytes(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "MrwhosethebossCommunity/1.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_json(self, status, payload):
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(204, {})

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"ok": True, "service": "community-backend"})
            return
        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if self.path != "/submit":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"ok": False, "error": "Invalid content length"})
            return

        if length <= 0 or length > MAX_BODY_SIZE:
            self.send_json(413, {"ok": False, "error": "Request body is too large or empty"})
            return

        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "Request must contain valid JSON"})
            return

        if not isinstance(data, dict):
            self.send_json(400, {"ok": False, "error": "Invalid request data"})
            return

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        category = str(data.get("category", "")).strip()
        message = str(data.get("message", "")).strip()

        if len(name) < 2:
            self.send_json(400, {"ok": False, "error": "Please enter your name."})
            return
        if len(name) > 100:
            self.send_json(400, {"ok": False, "error": "Name is too long."})
            return
        if not email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            self.send_json(400, {"ok": False, "error": "Please enter a valid email address."})
            return
        if len(email) > 254:
            self.send_json(400, {"ok": False, "error": "Email is too long."})
            return
        if category not in ALLOWED_CATEGORIES:
            self.send_json(400, {"ok": False, "error": "Please choose a valid category."})
            return
        if len(message) < 10:
            self.send_json(400, {"ok": False, "error": "Please write at least 10 characters."})
            return
        if len(message) > 2000:
            self.send_json(400, {"ok": False, "error": "Message is too long."})
            return

        submission = {
            "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
            "name": name,
            "email": email,
            "category": category,
            "message": message,
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }

        submissions = load_submissions()
        submissions.append(submission)
        save_submissions(submissions)

        self.send_json(201, {"ok": True, "message": "Submission received"})


if __name__ == "__main__":
    print(f"Community backend running on http://localhost:{PORT}")
    print("POST /submit  |  GET /health")
    HTTPServer((HOST, PORT), Handler).serve_forever()
