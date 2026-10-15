# API платежей

Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, Alembic. Суммы в API и БД указаны целым числом копеек.

## Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

API доступен по адресу `http://localhost:8000`. Миграции Alembic выполняются при запуске контейнера API. Они создают таблицы, но не добавляют тарифы и промокоды. Для работы примеров ниже заполните их:

```bash
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
INSERT INTO tariffs (title, price) VALUES
  ('basic', 990000),
  ('standard', 1990000),
  ('premium', 2990000)
ON CONFLICT (title) DO NOTHING;

INSERT INTO promocodes (name, discount) VALUES ('KVITTO10', 10)
ON CONFLICT (name) DO NOTHING;
SQL
docker compose restart api
```

Перезапуск API нужен для повторного чтения промокодов из БД.

## Тесты

```bash
docker compose exec api pytest -q
```

Тесты используют временную схему PostgreSQL и удаляют её после завершения.

## Примеры запросов

```bash
curl -i http://localhost:8000/tariffs

# Подставьте id тарифа standard из ответа GET /tariffs.
curl -i -X POST http://localhost:8000/payments \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: order-1' \
  -d '{"tariff_id":2,"email":"student@example.com","method":"installment","installment_months":3,"promo_code":"kvitto10"}'

# Подставьте id созданного платежа из ответа POST /payments.
curl -i http://localhost:8000/payments/1

# При первом вызове для этого payment_id поменяет статус, при повторном вызове выдаст ошибку
curl -i -X POST http://localhost:8000/webhooks/bank \
  -H 'Content-Type: application/json' \
  -d '{"payment_id":1,"status":"succeeded"}'
```
