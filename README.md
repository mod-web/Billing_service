### Собрать докер:
docker-compose up --build

### Проникнуть в контейнер:
docker-compose exec billing_service bash

### Создать миграции:
alembic revision --autogenerate -m "Database creation"

### Применить миграции - Разметить таблицы в БД:
alembic upgrade head
