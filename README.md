# СОЦИАЛЬНАЯ СЕТЬ MySyte
### Описание
Этот проект является социальной сетью под названием YATUBE. Здесь можно публиковать записи, подписываться\отписываться на других юзеров, комментировать записи. Все это возможно в этом проекте, но пока через API. В фронтенд мы пока не особо умеем, но скоро чтото да появится)
------------------------------------------------------------
### Используемые библиотеки:
- [Python 3.7+](https://www.python.org/)
- [Django 2.2.16](https://www.djangoproject.com)
- [Django Rest Framework 3.12.4](https://www.django-rest-framework.org)
- [Djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [SQLite3](https://www.sqlite.org/index.html)
------------------------------------------------------------
### Документация
После запуска проекта (*см. ниже) по адресу [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/) доступна документация к проекту.
------------------------------------------------------------
- ### Установка:
#### *Действия для юзеров Windows**

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/yandex-praktikum/kittygram.git
```
```
cd kittygram
```
Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
```
source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
------------------------------------------------------------
- ### Примеры запросов API
#### Регистрация
Эндпоинт: 
```
POST http://127.0.0.1:8000/api/v1/jwt/refresh/
```
Запрос:
```
{
    "username": "filengun",
    "password": "parol",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NjgxODkyMCwianRpIjoiMWYwMmQzNmQ2ODk1NGU1ZDljMzViYWZkYTE2MzMwOWUiLCJ1c2VyX2lkIjoyfQ.gHKBSRI93L8iHLf919FrFOWyo4khfXYY-9oBK2CgnT4"
}
```
Ответ:
```
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc1Mzc1ODEyLCJqdGkiOiIxNjVlNTBiMzBhNjc0YzZiOTQyZGM4Nzk3NjE1YmM0YiIsInVzZXJfaWQiOjJ9.TTUx5YFR9QsqZkE6t0ryR-mL_RjHWERIyhNbrT4zZPE"
}
```

#### Для того чтобы создать публикацию, необходимо аутентифицироваться и использовать:
Эндпоинт:
```
POST  http://127.0.0.1:8000/api/v1/posts/
```
А в body передать значения `"text", "image"(необязательно), "group"(необязательно)`.
```
{
    "text": "Я скажу не надо рая..."
}
```
Ответ:
```
{
    "id": 1,
    "author": "filengun2",
    "text": "Я скажу не надо рая...",
    "pub_date": "2022-10-25T22:18:56.622536Z",
    "image": null,
    "group": null
}
```
#### Для того чтобы обновить публикацию, юзаем:
Эндпоинт:
```
PUT  http://127.0.0.1:8000/api/v1/posts/{id}/
```
А в body передаем все теже `"text", "image"(необязательно), "group"(необязательно)`.
```
{
    "text": "Я скажу не надо рая... Дайте лучше родину мою"
}
```
Ответ:
```
{
    "id": 1,
    "author": "filengun2",
    "text": "Я скажу не надо рая... Дайте лучше родину мою",
    "pub_date": "2022-10-25T22:18:56.622536Z",
    "image": null,
    "group": null
}
```
#### Полный список запросов API находятся в [документации](#документация)
------------------------------------------------------------
- Создатель [Олег Борисович](https://github.com/Filengun)
