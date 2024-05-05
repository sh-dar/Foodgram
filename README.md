
# О проекте Foodgram:
Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Используемые технологии

* Django==3.2.16
* djangorestframework==3.14.0
* django_filter==22.1
* djoser==2.1.0
* drf-extra-fields==4.11.0
* flake8==6.0.0
* flake8-isort==6.0.0
* Pillow==9.3.0
* python-dotenv==1.0.1

## Инструкция по запуску проекта

**Клонировать репозиторий:**
```
git clone git@github.com:sh-dar/foodgram-project-react.git
```
**Установить и активировать виртуальное окружение:**
для MacOS:
```
python3 -m venv venv
source venv/bin/activate
```

для Windows:
```
python -m venv venv
source venv/Scripts/activate
```
**Установить зависимости:**
```
pip install -r requirements.txt
```
**Применить миграции:**
```
python manage.py migrate
```
**Загрузить данные в БД:**

В папке data подготовлен список тегов и ингредиентов с единицами измерения.
```
python manage.py load_tags
python manage.py load_ingredients
```
**Запустить сервер:**
```
python manage.py runserver
```

## Спецификация API
В папке infra выполните команду
```
docker-compose up
```
Спецификация станет доступна по адресу:
http://localhost/api/docs/

### Автор
[Dari Sharapova - sh-dar](https://github.com/sh-dar)
