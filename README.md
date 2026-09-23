# Сайт ЦТП «Орех» СВФУ

Сайт Центра технологического предпринимательства «Орех» Арктического инновационного центра СВФУ:
информация о центре, достижения, услуги, резиденты, локация, этапы отбора и форма заявки.

Стек: Python 3, Flask, Jinja2, SQLite, HTML, CSS, JavaScript.

## Структура

```
app.py               приложение Flask: маршруты, проверка формы, работа с базой
schema.sql           структура базы данных (таблица applications)
data/residents.json  сведения о резидентах
templates/           шаблоны страниц (base.html, index.html)
static/css/          стили
static/js/           переключение карточек резидентов
static/img/          логотипы и фотографии
instance/            файл базы данных (создаётся автоматически, в git не попадает)
```

## Запуск на компьютере

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Сайт откроется по адресу http://127.0.0.1:5000

## Просмотр заявок

```bash
flask --app app applications
```

База данных лежит в `instance/oreh.sqlite3`, её также можно открыть в DB Browser for SQLite.

## Размещение на PythonAnywhere (бесплатно)

1. Загрузите проект на GitHub (см. ниже) и зарегистрируйтесь на pythonanywhere.com.
2. В разделе **Consoles** откройте Bash и выполните:
   ```bash
   git clone https://github.com/<логин>/<репозиторий>.git oreh-site
   cd oreh-site
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. В разделе **Web** нажмите **Add a new web app** → **Manual configuration** → Python 3.
4. В поле **Virtualenv** укажите `/home/<логин>/oreh-site/.venv`.
5. Откройте **WSGI configuration file** и замените содержимое на:
   ```python
   import os, sys
   path = "/home/<логин>/oreh-site"
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ["OREH_SECRET_KEY"] = "придумайте-длинную-случайную-строку"
   from app import app as application
   ```
6. В блоке **Static files** добавьте: URL `/static/`, Directory `/home/<логин>/oreh-site/static`.
7. Нажмите **Reload**. Сайт будет доступен по адресу `https://<логин>.pythonanywhere.com`.

Обновление после изменений: `git pull` в консоли PythonAnywhere и кнопка **Reload**.

## Загрузка на GitHub

```bash
git init
git add .
git commit -m "Сайт ЦТП «Орех»"
git branch -M main
git remote add origin https://github.com/<логин>/<репозиторий>.git
git push -u origin main
```

## Настройки

| Переменная        | Назначение                                       |
|-------------------|--------------------------------------------------|
| `OREH_SECRET_KEY` | секретный ключ сессий; обязателен на сервере      |
| `OREH_DATABASE`   | путь к файлу базы (по умолчанию `instance/oreh.sqlite3`) |
