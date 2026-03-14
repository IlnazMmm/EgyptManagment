# Migrations

SQL-миграции для PostgreSQL.

Порядок выполнения: по имени файла (`001_*.sql`, `002_*.sql`, ...).

В Docker Compose начальная миграция `001_init.sql` автоматически выполняется через
`docker-entrypoint-initdb.d` при первом старте контейнера Postgres.
