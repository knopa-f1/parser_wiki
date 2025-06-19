# Parser Wiki

Асинхронное FastAPI-приложение для рекурсивного парсинга статей Википедии с сохранением в PostgreSQL и генерацией
краткого содержания с помощью OpenAI GPT.

---

## Возможности

- Рекурсивный парсинг статьи с Википедии до 5 уровней в глубину
- Ограничение количества ссылок на уровень
- Исключение технических и служебных страниц
- Сохранение статей и связей в PostgreSQL
- Генерация summary статьи с использованием GPT-4o
- REST API для запуска парсинга и получения summary

---

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/knopa-f1/parser_wiki.git
cd parser_wiki
```

### 2. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=my_db

MODE=DEV

LANG=ru
MAX_DEPTH=5
MAX_LINKS_PER_LEVEL=3

OPENAI_API_KEY=your_openai_api_key
```

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

Приложение будет доступно по адресу:  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## Примеры API

### Запустить парсинг

```http
POST /parse?url=https://ru.wikipedia.org/wiki/Животные
```

### Получить краткое содержание

```http
GET /summary?url=https://ru.wikipedia.org/wiki/Животные
```

---

## Ограничения

- Парсинг ограничен до 5 уровней и 3 ссылок на уровень по умолчанию (см. `.env`)
- Исключаются технические страницы, такие как `Служебная:`, `Категория:`, `Template:` и др.
- Генерация summary выполняется только для корневой статьи
