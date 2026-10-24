"""Маршруты приложения и проверка данных. Часть студент1."""

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


@app.get("/applications/<int:application_id>")
def detail(application_id):
    return render_template("detail.html", application=find_application(application_id))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    data = dict(find_application(application_id))
    error = None
    if request.method == "POST":
        data, error = read_form()
        if error is None:
            database.update(application_id, data)
            return redirect(url_for("detail", application_id=application_id))
    return render_template(
        "form.html", data=data, error=error, page_title="Редактирование заявки",
        categories=CATEGORIES, priorities=PRIORITIES
    ), 400 if error else 200


@app.post("/applications/<int:application_id>/delete")
def delete_application(application_id):
    find_application(application_id)
    database.delete(application_id)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
