"""Сайт Центра технологического предпринимательства «Орех» СВФУ.

Запуск для разработки:
    python app.py
"""
import json
from datetime import date
import os
import re
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("OREH_DATABASE", BASE_DIR / "instance" / "oreh.sqlite3"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("OREH_SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # форма небольшая, крупные запросы не нужны

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- база данных ----------

def get_db() -> sqlite3.Connection:
    if "db" not in g:
        DATABASE.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Создаёт таблицы, если их ещё нет."""
    with app.app_context():
        schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
        get_db().executescript(schema)
        get_db().commit()


# ---------- данные страницы ----------

def load_residents() -> list[dict]:
    with open(BASE_DIR / "data" / "residents.json", encoding="utf-8") as f:
        return json.load(f)


RESIDENTS = load_residents()


# ---------- защита формы от подделки запросов (CSRF) ----------

def csrf_token() -> str:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.context_processor
def inject_year():
    return {"current_year": date.today().year}


# ---------- проверка заявки ----------

def validate_application(form) -> tuple[dict, dict]:
    data = {
        "full_name": form.get("full_name", "").strip(),
        "phone": form.get("phone", "").strip(),
        "email": form.get("email", "").strip(),
        "description": form.get("description", "").strip(),
    }
    errors = {}
    if not 2 <= len(data["full_name"]) <= 200:
        errors["full_name"] = "Укажите ФИО."
    if not 6 <= len(data["phone"]) <= 40:
        errors["phone"] = "Укажите телефон."
    if not EMAIL_RE.match(data["email"]) or len(data["email"]) > 200:
        errors["email"] = "Проверьте адрес почты."
    if not 10 <= len(data["description"]) <= 4000:
        errors["description"] = "Опишите проект хотя бы парой предложений."
    return data, errors


# ---------- маршруты ----------

@app.get("/")
def index():
    return render_template("index.html", residents=RESIDENTS, form={}, errors={})


@app.post("/apply")
def apply():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)

    data, errors = validate_application(request.form)
    if errors:
        return render_template("index.html", residents=RESIDENTS, form=data, errors=errors), 422

    db = get_db()
    db.execute(
        "INSERT INTO applications (full_name, phone, email, project_description) VALUES (?, ?, ?, ?)",
        (data["full_name"], data["phone"], data["email"], data["description"]),
    )
    db.commit()
    flash("Мы свяжемся с вами, чтобы назначить очную встречу.", "success")
    return redirect(url_for("index", _anchor="apply"))


@app.errorhandler(400)
def bad_request(_e):
    flash("Страница устарела, отправьте форму ещё раз.", "error")
    return redirect(url_for("index", _anchor="apply"))


@app.cli.command("applications")
def list_applications():
    """Показать поступившие заявки: flask --app app applications"""
    rows = get_db().execute(
        "SELECT id, created_at, full_name, phone, email, project_description FROM applications ORDER BY id DESC"
    ).fetchall()
    if not rows:
        print("Заявок пока нет.")
    for r in rows:
        print(f"#{r['id']}  {r['created_at']}  {r['full_name']}  {r['phone']}  {r['email']}")
        print(f"    {r['project_description']}\n")


init_db()

if __name__ == "__main__":
    app.run(debug=True)
