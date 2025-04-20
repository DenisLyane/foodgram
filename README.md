1. Проект Foodgram
«Foodgram» — сайт "кулинарная книжкка". 

2. Список технологий:
Язык программирования: Python

Фреймворк: Django

База данных: PostgreSQL

API: Django Rest Framework

Сервер: Nginx

WSGI-сервер: Gunicorn

Контейнеризация: Docker

3. Что нужно для запуска проекта:
Клонировать репозиторий и перейти в него в командной строке

Cоздать, активировать и обновить виртуальное окружение:
для Windows

python -m venv venv 
source venv/Scripts/activate
python -m pip install --upgrade pip

Linux/macOS

python3 -m venv venv 
source venv/bin/activate
python3 -m pip install --upgrade pip

Установить зависимости из файла requirements.txt:
pip install -r requirements.txt

Запуск проекта с помощью Docker:
Подключиться на удалённый сервер.
На сервере создать директорию foodgram и перейти в нее.

sudo mkdir foodgram/ 
cd foodgram

Скопировать файл docker-compose.production.yml из текущего репозитория в корневую папку проекта foodgram/ на сервере (или создать его и скопировать код).
В корневой папке проекта foodgram/ создать файл .env и заполните его согласно примеру:

POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
DB_HOST=db
DB_PORT=5432
SECRET_KEY = *key*
DEBUG = True
ALLOWED_HOSTS = 127.0.0.1,localhost

Выполните git push Создайте администратора сайта sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

4. Ссылка на документацию:
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

5. Автор проекта:
Ляне Денис