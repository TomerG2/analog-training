#!/usr/bin/env python3
import http.server
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.db")
PORT = 8742


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime')),
            lesson TEXT NOT NULL,
            phase INTEGER NOT NULL,
            round INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            response_time REAL NOT NULL,
            target_time TEXT,
            user_answer TEXT,
            session_id TEXT
        )
    """)
    conn.commit()
    conn.close()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/results":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                """INSERT INTO results (lesson, phase, round, correct, response_time,
                   target_time, user_answer, session_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    body["lesson"],
                    body["phase"],
                    body["round"],
                    body["correct"],
                    body["response_time"],
                    body.get("target_time"),
                    body.get("user_answer"),
                    body.get("session_id"),
                ),
            )
            conn.commit()
            conn.close()
            self._json_response(201, {"ok": True})
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/results":
            params = parse_qs(parsed.query)
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM results"
            args = []
            if "lesson" in params:
                query += " WHERE lesson = ?"
                args.append(params["lesson"][0])
            query += " ORDER BY timestamp ASC"
            rows = conn.execute(query, args).fetchall()
            conn.close()
            self._json_response(200, [dict(r) for r in rows])
        elif parsed.path == "/api/sessions":
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT session_id, lesson, phase,
                       MIN(timestamp) as started_at,
                       COUNT(*) as rounds,
                       SUM(correct) as correct_count,
                       ROUND(AVG(response_time), 2) as avg_response_time,
                       ROUND(100.0 * SUM(correct) / COUNT(*), 1) as accuracy_pct
                FROM results
                GROUP BY session_id
                ORDER BY started_at DESC
            """).fetchall()
            conn.close()
            self._json_response(200, [dict(r) for r in rows])
        else:
            super().do_GET()

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(format, *args)


if __name__ == "__main__":
    init_db()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(("", PORT), Handler)
    print(f"Teaching server running at http://localhost:{PORT}")
    print(f"Dashboard:  http://localhost:{PORT}/dashboard.html")
    print(f"Lessons:    http://localhost:{PORT}/lessons/")
    print(f"Database:   {DB_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
