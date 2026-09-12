# FastAPI Todo & Analytics Service

Асинхронный backend-сервис для управления задачами (todos), аутентификации пользователей, работы с вложениями и фоновой аналитикой. Реализация [задания](https://stepik.org/lesson/1044678/step/16?unit=1053252).

##  Технологический стек

- **Backend**: Python 3.12+, FastAPI, Uvicorn
- **Управление зависимостями**: uv
- **База данных**: PostgreSQL 18
- **Брокер задач**: Redis 8
- **Хранилище файлов**: MinIO (S3-compatible)
- **Фоновые задачи**: Taskiq
- **Инфраструктура**: Docker, Docker Compose
- **Мониторинг**: Prometheus, Grafana, Loki

##  Основные возможности

-  **Аутентификация**: Регистрация, вход, обновление и отзыв токенов (JWT).
-  **Управление задачами**: CRUD операции для todos.
-  **Вложения**: Загрузка и скачивание файлов через presigned URLs (MinIO).
-  **Аналитика**: Асинхронный расчёт аналитики через фоновые воркеры (Taskiq).
-  **Импорт/Экспорт**: Фоновая обработка файлов с данными.
-  **Мониторинг**: Встроенные метрики (Prometheus) и централизованные логи (Loki).

##  Быстрый старт

### 1. Требования
- Установленный [Docker](https://www.docker.com/) и Docker Compose
- Установленный [uv](https://docs.astral.sh/uv/) (для локального запуска API)

### 2. Настройка окружения
Скопируйте файл с переменными окружения и заполните его своими значениями:

    cp .env.example .env
    cp .env.worker.example .env.worker

### 3. Запуск инфраструктуры
Поднимите базы данных, брокер, хранилище и системы мониторинга:

    docker compose up -d

### 4. Запуск приложения
Запустите основной API-сервер локально (или через Docker, если настроено):

    uv run fastapi dev main.py 

*Фоновый воркер Taskiq запустится автоматически внутри Docker-контейнера worker.*

### 5. Проверка
- **Swagger UI**: http://localhost:8000/docs
- **Healthcheck**: http://localhost:8000/health
- **Метрики**: http://localhost:8000/metrics

## Мониторинг

Проект включает готовый стек наблюдения:

| Сервис | URL | Логин / Пароль         |
|--------|-----|------------------------|
| **Grafana** | http://localhost:3000 | admin / {GRAFANA_PASS} |
| **Prometheus** | http://localhost:9090 | Без авторизации        |
| **MinIO Console** | http://localhost:9001 | {S3_USER} / {S3_PASS}  |


##  Структура проекта 

    .
    ├── app/
    │   ├── api/            # Роутеры (auth, todos, analytics, attachments, ...)
    │   ├── database/       # Модели SQLAlchemy, схемы, настройки БД
    │   ├── errors/         # Исключения и хэндлеры
    │   ├── repos/          # Репозитории для взаимодействия с БД
    │   ├── services/       # Сервисы
    │   └── utils/          # Утилиты (S3 менеджер, Taskiq брокер, Лог менеджер ...)
    ├── prometheus/         # Конфигурация Prometheus
    ├── loki/               # Конфигурация Loki
    ├── docker-compose.yml  # Оркестрация сервисов
    └── README.md
    └── main.py             # Точка входа FastAPI
