# Веб-приложение

## Запуск для разработчика

Скачайте репозиторий:
```
git clone https://github.com/aleksioprime/sk-empolimer.git
cd empolimer
```

Запустите сервис локально:
```
cd web
docker-compose -p empolimer up -d --build
```

Если выходит ошибка `exec /usr/src/app/entrypoint.sh: permission denied`, то нужно вручную установить флаг выполнения для entrypoint.sh в локальной системе:
```
chmod +x backend/entrypoint.sh
chmod +x auth/entrypoint.sh
```

Создание миграциий:
```shell
docker exec -it empolimer-backend alembic revision --autogenerate -m "init migration"
```

Применение миграции (при перезапуске сервиса делается автоматически):
```shell
docker exec -it empolimer-backend alembic upgrade head
```

Создание суперпользователя:
```shell
docker-compose -p empolimer exec backend python scripts/create_superuser.py \
  --username superuser \
  --password 1q2w3e \
  --email admin@empolimer.ru
```

### Данные брокера:

логин: empolimer
пароль: Techno2025

### Данные Node-Red:

логин: admin
пароль: 12345678

### Проверка:

1. Установите утилиту mosquitto:

```
brew install mosquitto
```

2. Подпишитесь на топик в одном терминале:

```
mosquitto_sub -h localhost -p 1883 -t "devices/551b1578-2f39-49d5-b44e-0d0b42454b24/air" -i sub_test -u empolimer -P Techno2025 -v
```

3. Отправьте сообщение в топик в другом терминале:
```
mosquitto_pub -h localhost -p 1883 -t "devices/demo_2/air" -i pub_test -u empolimer -P Techno2025 -m '{"datetime":"2025-06-26T21:41:38+12","temp":15.3,"hum":15.0}'
```


# Запуск на сервере:

## Подготовка сервера

Установите сервер с ОС Ubuntu 22.04+

Выполните обновление пакетов:
```
sudo apt update && sudo apt upgrade -y
```

Установите Docker:
```
sudo apt update && sudo apt install -y docker.io
```

Установите Compose-плагин:
```
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

Проверьте установку
```
docker compose version
```

## Переменные окружения

Переменные окружения берутся из репозитория.

Для загрузки контейнеров в Docker Hub используется:
```
DOCKER_HUB_USERNAME=<логин пользователя Docker Hub>
DOCKER_HUB_ACCESS_TOKEN=<access-токен, который был выдан в DockerHub>
```

Для деплоя приложения из репозитория на сервер используется:
```
SERVER_HOST=<IP-адрес сервера>
SERVER_SSH_KEY=<Приватный ключ для подключения к серверу по SSH>
SERVER_USER=<Имя пользователя сервера>
```

Для сервиса создаётся переменная `ENV_VARS`, куда записываются все переменные из `.env.example`

## Добавление бесплатного SSL-сертификата

В контейнер фронтенда добавлен CertBot, с помощью которого происходит регистрация сертификата

Проверьте установку:
```
docker exec -it empolimer-front certbot --version
```

Запустите CertBot для получения сертификатов
```
docker exec -it empolimer-front certbot --nginx -d empolimer.ru -d www.empolimer.ru
ls -l /etc/letsencrypt/live/empolimer.ru/
```

Добавьте автообновление сертификатов (каждые 90 дней). Для этого откройте crontab:
```
sudo crontab -e
```

Добавьте строку:
```
0 3 * * * docker exec empolimer-front certbot renew --quiet && docker exec empolimer-front nginx -s reload
```

Удаление сертификатов:
```
docker exec -it empolimer-front rm -rf /etc/letsencrypt/renewal/empolimer.ru.conf
docker exec -it empolimer-front rm -rf /etc/letsencrypt/live/empolimer.ru
docker exec -it empolimer-front rm -rf /etc/letsencrypt/archive/empolimer.ru
```