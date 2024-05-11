
# О проекте Foodgram:
Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Используемые технологии
* Python 3.9
* Django 3.2
* Django Rest Framework 3.14
* Djoser 2.1
* Python-dotenv 1.0 ###############

## Инструкция по запуску проекта

**Клонировать репозиторий:**
```
git clone git@github.com:sh-dar/foodgram-project-react.git
```
**Установить и активировать виртуальное окружение:**
* Перейти в папку проекта
```
cd foodgram-project-react
```
* для MacOS:
```
python3 -m venv venv
source venv/bin/activate
```

* для Windows:
```
python -m venv venv
source venv/Scripts/activate
```
**Установить зависимости:**
```
pip install -r requirements.txt
```
**Применить миграции:**
* Перейти в папку c файлом manage.py 
```
cd backend/foodgram
```
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
[Документация API](http://localhost/api/docs/)

### Автор
[Dari Sharapova - sh-dar](https://github.com/sh-dar)
