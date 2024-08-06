[![Main Foodgram workflow](https://github.com/sh-dar/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/sh-dar/foodgram-project-react/actions/workflows/main.yml)

# About the Foodgram project:
The Foodgram is a website for publishing and sharing recipes. Authorized users can subscribe to their favorite authors, add recipes to their favorites and shopping list, and download the shopping list. Unregistered users have access to registration, authorization, and viewing other users' recipes.

## Technologies

* Python 3.9
* Django 3.2
* Django Rest Framework 3.14
* Djoser 2.1
* Python-dotenv 1.0
* Docker
* Postgres

## Server Setup

1. Connect to the remote server:

    ```
    ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME USERNAME@SERVER_IP_ADDRESS
    ```

    Where:
    - `PATH_TO_SSH_KEY` - the path to your SSH key file
    - `SSH_KEY_NAME` - the name of your SSH key file
    - `USERNAME` - your username on the server
    - `SERVER_IP_ADDRESS` - the IP address of your server

2. Install Docker Compose on the server:

    ```
    sudo apt update
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose
    ```

3. Create a `foodgram` directory on the server:

    ```
    mkdir foodgram && cd foodgram/
    ```

4. Create an `.env` file in the `foodgram/` directory on the server. 
    All necessary variables are listed in the `.env.example` file located in the root directory of the project.
    ```
    touch .env
    ```

5. Copy the `docker-compose.production.yml` and `nginx.conf` files from the `infra` directory to the `foodgram/` directory on the server:

    ```
    scp infra/docker-compose.production.yml infra/nginx.conf USERNAME@SERVER_IP_ADDRESS:/home/USERNAME/foodgram/
    ```

6. Start Docker Compose:

    ```
    sudo docker-compose -f docker-compose.production.yml up -d
    ```

## CI/CD Setup

1. The workflow file is located in the directory:

    ```
    /.github/workflows/main.yml
    ```

2. Set up Secrets and variables for Actions in your GitHub settings:

    ```
    DOCKER_USERNAME                # DockerHub username
    DOCKER_PASSWORD                # DockerHub password
    HOST                           # Server IP address
    USER                           # Username
    SSH_KEY                        # Content of the private SSH key (cat ~/.ssh/id_rsa)
    SSH_PASSPHRASE                 # Password for the SSH key

    TELEGRAM_TO                    # Your Telegram account ID (you can get it from @userinfobot, command /start)
    TELEGRAM_TOKEN                 # Your bot token (you can get the token from @BotFather, command /token, bot name)
    ```

## Local Setup

1. Clone the repository:

    ```
    git clone git@github.com:sh-dar/foodgram-project-react.git
    ```

2. Install and activate the virtual environment:

    Go to the project folder

    ```
    cd foodgram-project-react
    ```

    for MacOS:
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

    for Windows:
    ```
    python -m venv venv
    source venv/Scripts/activate
    ```

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Apply migrations

    Go to the folder with the manage.py file 
    ```
    cd backend/foodgram/
    ```
    ```
    python manage.py migrate
    ```

5. Load data into the database:

    In the data folder, there is a prepared list of tags and ingredients with units of measurement.
    ```
    python manage.py load_tags
    python manage.py load_ingredients
    ```

6. Start the server:

    ```
    python manage.py runserver
    ```

## API Specification
In the infra folder, run the command
```
docker-compose up
```
The specification will be available at:
[API Documentation](http://localhost/api/docs/)


### Author
[Dari Sharapova - sh-dar](https://github.com/sh-dar)
