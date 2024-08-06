[![Main Foodgram workflow](https://github.com/sh-dar/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/sh-dar/foodgram-project-react/actions/workflows/main.yml)

# О проекте Foodgram:
Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Используемые технологии

* Python 3.9
* Django 3.2
* Django Rest Framework 3.14
* Djoser 2.1
* Python-dotenv 1.0
* Docker
* Postgres

## Инструкция по запуску проекта на сервере

1. Подключиться к удаленному серверу:

    ```
    ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME USERNAME@SERVER_IP_ADDRESS
    ```

    Где:
    - `PATH_TO_SSH_KEY` - путь к файлу с вашим SSH-ключом
    - `SSH_KEY_NAME` - имя файла с вашим SSH-ключом
    - `USERNAME` - ваше имя пользователя на сервере
    - `SERVER_IP_ADDRESS` - IP-адрес вашего сервера

2. Установить Docker Compose на сервер:

    ```
    sudo apt update
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose
    ```

3. Создать на сервере директорию `foodgram`:

    ```
    mkdir foodgram && cd foodgram/
    ```

4. Создать файл `.env` в директории `foodgram/` на сервере. 
    Все необходимые переменные перечислены в файле `.env.example`, который находится в корневой директории проекта.
    ```
    touch .env
    ```

5. Скопируйте файлы `docker-compose.production.yml` и `nginx.conf` из директории `infra` в директорию `foodgram/` на сервере:

    ```
    scp infra/docker-compose.production.yml infra/nginx.conf USERNAME@SERVER_IP_ADDRESS:/home/USERNAME/foodgram/
    ```

6. Запустите Docker Compose:

    ```
    sudo docker-compose -f docker-compose.production.yml up -d
    ```

## Настройка CI/CD

1. Файл workflow находится в директории:

    ```
    /.github/workflows/main.yml
    ```

2. Настройте Secrets and variables для Actions в настройках своего гитхаба:

    ```
    DOCKER_USERNAME                # имя пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    HOST                           # IP-адрес сервера
    USER                           # имя пользователя
    SSH_KEY                        # содержимое приватного SSH-ключа (cat ~/.ssh/id_rsa)
    SSH_PASSPHRASE                 # пароль для SSH-ключа

    TELEGRAM_TO                    # ID вашего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен вашего бота (получить токен можно у @BotFather, команда /token, имя бота)
    ```

## Инструкция по запуску проекта локально

1. Клонировать репозиторий:

    ```
    git clone git@github.com:sh-dar/foodgram.git
    ```

2. Установить и активировать виртуальное окружение:

    Перейти в папку проекта

    ```
    cd foodgram
    ```

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

3. Установить зависимости:

    ```
    pip install -r requirements.txt
    ```

4. Применить миграции

    Перейти в папку c файлом manage.py 
    ```
    cd backend/foodgram/
    ```
    ```
    python manage.py migrate
    ```

5. Загрузить данные в БД:

    В папке data подготовлен список тегов и ингредиентов с единицами измерения.
    ```
    python manage.py load_tags
    python manage.py load_ingredients
    ```

6. Запустить сервер:

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
