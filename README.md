## Проект предоставляет возможность запустить через systemd и docker
### 1. Как запустить проект через systemd:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/dkutuzovcloud/kittygram_dkutuzov_cats_events.git
```
Переходим в директорию с проектом
```
cd ~/kittygram/kittygram_dkutuzov
```
Установка зависимостей
```
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-venv python3.11-dev nginx supervisor -y
python3.11 -m venv venv
source venv/bin/activate
python3.11 manage.py migrate
pip install -r requirements.txt
deactivate
```
Запуск приложения через systemd
```
sudo nano /etc/systemd/system/kittygram.service
```
Содержимое systemd.service
```
[Unit]
Description=Kittygram Gunicorn dkutuzov
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/kittygram/kittygram_dkutuzov
Environment="PATH=/root/kittygram/kittygram_dkutuzov/venv/bin"
ExecStart=/root/kittygram/kittygram_dkutuzov/venv/bin/gunicorn \
          --bind 0.0.0.0:8000 \
          kittygram.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```
Запуск Gunicorn
```
sudo systemctl daemon-reload
sudo systemctl start kittygram
sudo systemctl enable kittygram
sudo systemctl status kittygram
```
Настройка nginx
```
sudo nano /etc/nginx/sites-available/kittygram
```

Содержимое файла kittygram
```
server {
    listen 8443;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Создание симлинка, проверка конфига и запуск
```
sudo ln -s /etc/nginx/sites-available/kittygram /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```
Сервис будет доступен по порту который указан в /etc/nginx/sites-available/kittygram, пример:
```
listen 8443
```
Проверка работы
```
POST -  curl -X POST http://localhost:8443/cats/   -H "Content-Type: application/json"   -d '{"name":"Мурка","color":"gray","birth_year":2020}'
GET - curl http://localhost:8443/cats/
```


### 2. Как запустить проект через docker:

```
git clone https://github.com/dkutuzovcloud/kittygram_dkutuzov_cats_events.git

```
Переходим в директорию с проектом
```
cd ~/kittygram/kittygram_dkutuzov
```
Установка docker.io и docker compose
```
apt install docker.io
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v5.0.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

```
Редактирование .env
```
DOCKER_IMAGE=dkutuzov/kittygram_dkutuzov:latest

APP_PORT=8081 - - можно заменить на свой порт
NGINX_PORT=8443 - можно заменить на свой порт
```
Содержимое docker-compose.yml
```
version: '3.8'

services:
  kittygram:
    image: ${DOCKER_IMAGE}
    ports:
      - "${APP_PORT}:8000"
    restart: always
    volumes:
      - kittygram_data:/app

  nginx:
    image: nginx:alpine
    ports:
      - "${NGINX_PORT}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - kittygram
    restart: always

volumes:
  kittygram_data:

```
Запуск docker-compose.yml
```
docker-compose up -d
```
Сервис будет доступен по порту который указан в .env
```
NGINX_PORT=8443
```
Проверка работы
```
POST -  curl -X POST http://localhost:8443/cats/   -H "Content-Type: application/json"   -d '{"name":"DockerМурка","color":"blue","birth_year":2023}'
GET - curl http://localhost:8443/cats/
```
