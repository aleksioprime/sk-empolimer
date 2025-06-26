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