# BakeCake

BakeCake — сайт для приёма заказов на кастомные и готовые торты. Проект построен на Django и использует серверные шаблоны, SQLite для MVP, оплату через ЮKassa в тестовом режиме и личный кабинет клиента.

## Запуск

Для запуска проекта понадобится Python 3.12+ и виртуальное окружение.

Установите зависимости:

```sh
pip install -r requirements.txt
```

Примените миграции:

```sh
python manage.py migrate
```

Запустите локальный сервер:

```sh
python manage.py runserver
```

После запуска сайт будет доступен по адресу `http://127.0.0.1:8000/`.

## Переменные окружения

Часть настроек проекта берётся из `.env` рядом с `manage.py`.

Доступные переменные:

- `SECRET_KEY` — секретный ключ Django.
- `DEBUG` — режим отладки.
- `YOOKASSA_SHOP_ID` — идентификатор магазина ЮKassa.
- `YOOKASSA_SECRET_KEY` — секретный ключ ЮKassa.
- `YOOKASSA_RETURN_URL` — URL возврата после оплаты.
- `TG_TOKEN` — токен Telegram-бота.
- `ADMIN_CHAT_ID` — chat id для отправки кода подтверждения.
- `SMS_API_KEY` — ключ SMS-сервиса, если будет использоваться.
- `SMS_SENDER_NAME` — имя отправителя SMS.
- `JIVOSITE_WIDGET_ID` — идентификатор виджета JivoSite.
