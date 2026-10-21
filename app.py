"""Маршруты приложения и проверка данных"""

from flask import Flask, abort, redirect, render_template, request, url_for

import database

app = Flask(__name__)
database.init_db()

CATEGORIES = ("Веб-приложение", "Десктопное приложение", "Анализ данных")
PRIORITIES = ("Низкий", "Средний", "Высокий")
FIELDS = ("full_name", "group_name", "project_title", "description", "category", "priority")


def read_form():
    data = {field: request.form.get(field, "").strip() for field in FIELDS}
    if any(not value for value in data.values()):
        return data, "Заполните все поля."
    if data["category"] not in CATEGORIES or data["priority"] not in PRIORITIES:
        return data, "Выберите допустимые категорию и приоритет."
    return data, None


def find_application(application_id):
    application = database.get_by_id(application_id)
    if application is None:
        abort(404)
    return application


@app.get("/")
def index():
    return render_template("list.html", applications=database.get_all())


@app.route("/applications/new", methods=["GET", "POST"])
def create_application():
    data = {}
    error = None
    if request.method == "POST":
        data, error = read_form()
        if error is None:
            application_id = database.create(data)
            return redirect(url_for("detail", application_id=application_id))
    return render_template(
        "form.html", data=data, error=error, page_title="Новая заявка",
        categories=CATEGORIES, priorities=PRIORITIES
    ), 400 if error else 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
