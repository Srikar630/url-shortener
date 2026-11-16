"""Simple URL shortener with Flask and SQLite."""
import random
import sqlite3
import string
from urllib.parse import urlparse

from flask import Flask, redirect, render_template_string, request, abort

app = Flask(__name__)
DB = "urls.db"

PAGE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>URL Shortener</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:520px;margin:3rem auto;padding:0 1rem}
 input{width:70%;padding:.5rem} button{padding:.5rem 1rem}
 .err{color:#b91c1c}
</style></head>
<body>
<h1>URL Shortener</h1>
<form method="post">
  <input name="url" placeholder="https://example.com/very/long/link" required>
  <button>Shorten</button>
</form>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
{% if short %}<p>Short link: <a href="{{ short }}">{{ short }}</a></p>{% endif %}
</body></html>
"""


def get_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, url TEXT NOT NULL)")
    return conn


def make_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def valid_url(url):
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.netloc)


@app.route("/", methods=["GET", "POST"])
def index():
    short = error = None
    if request.method == "POST":
        url = request.form["url"].strip()
        if not valid_url(url):
            error = "Please enter a valid URL starting with http:// or https://"
        else:
            code = make_code()
            with get_db() as db:
                db.execute("INSERT INTO urls VALUES (?, ?)", (code, url))
            short = request.host_url + code
    return render_template_string(PAGE, short=short, error=error)


@app.route("/<code>")
def go(code):
    with get_db() as db:
        row = db.execute("SELECT url FROM urls WHERE code = ?", (code,)).fetchone()
    if not row:
        abort(404)
    return redirect(row[0])


if __name__ == "__main__":
    app.run(debug=True)
