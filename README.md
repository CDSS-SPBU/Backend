Струткура проекта

```
medical_support_project/
├── docs_processing/           # Первичная обработка документов
│   ├── upload_files.py        # Загрузка документов с сайта клинических рекомендаций
│   ├── pdf_parser.py          # Парсер документов
│   └── text_cleaner.py        # Исправление ошибок
├── db/                        # Работа с БД
│   ├── postgres.py            # Хранение исходных документов
│   └── vector_db.py           # Qdrant/Weaviate/Chroma
├── api/                       # Директория с API-роутами
│   ├── router_page.py         # Роуты для страниц
│   └── router_socket.py       # Роуты для WebSocket-соединений
├── services/                  # Основные взаимодействия с пользователем
│   ├── chat_service.py
│   └── document_service.py
├── requirements.txt           # Файл зависимостей проекта
├── .env                       # Переменные окружения
└── main.py                    # Запуск приложения
```

Так как у меня проблемы с загрузкой модели, которые идут сразу при запуске rerank-service/app.py и embedding-service/app.py я не могу проверить работу вебсокета.
При ручном запуске этих файлов без загрузки модели роуты отвечают. 
Необходимо проверить работоспособность api/router-soket.py функцию get_responce
И также работоспособность докера 

## Запуск приложения

### Локально

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Подготовьте переменные окружения (создайте файл `.env` с параметрами подключения):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=clinical_recommendations
   DB_USER=postgres
   DB_PASSWORD=qwerty
   EMBEDDING_SERVICE_URL=http://localhost:8000/embed
   RERANK_SERVICE_URL=http://localhost:8001/rerank
   VECTOR_DB_HOST=localhost
   VECTOR_DB_PORT=5433
   VECTOR_DB_NAME=rag
   VECTOR_DB_USER=dev
   VECTOR_DB_PASSWORD=dev_password
   LLM_SERVICE_URL=http://localhost:8003/generate
   RAG_RETRIEVAL_LIMIT=20
   ```
3. Инициализируйте БД:
   ```bash
   python -m db.init_db
   ```
4. Запустите сервер:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8002
   ```
5. Проверка:
   - HTTP: `curl http://localhost:8002/`
   - WebSocket: подключение к `ws://localhost:8002/ws/chat`

### Через Docker

1. Убедитесь, что embedding-service и rerank-service работают на хосте (порты 8000 и 8001).
2. Поднимите контейнеры:
   ```bash
    docker compose up --build
   ```
   Приложение будет доступно на `http://localhost:8002`.
3. При необходимости переопределите переменные окружения через `.env` файл или экспорт в терминале (см. секцию выше). Переменные `EMBEDDING_SERVICE_URL`, `RERANK_SERVICE_URL` и `LLM_SERVICE_URL` по умолчанию смотрят на host-машину через `host.docker.internal`.

## Проверка работоспособности

- **HTTP эндпоинты** – `GET /`, `GET /doclist/paginated`, `POST /createdoc`, `GET /doclist/{doc_id}`, `DELETE /doclist/{doc_id}`.
- **WebSocket** – отправьте сообщение вида:
  ```json
  {"type": "chat_message", "query": "Чем лучше лечить пациента с защемлением позвоночного нерва?"}
  ```
-  Бэкенд последовательно вызывает embedding-service, ищет 20 ближайших чанков в БД, переранжирует их в rerank-service и передаёт в LLM-сервис. В чат вернётся итоговый ответ с цитатами источников.
- **Модельные сервисы** – следуйте инструкциям в `TESTING_GUIDE.md` для проверки `embedding-service` и `rerank-service`.

## Фронтенд

- UI находится в `Frontend/` (Vue 3). Для локального запуска:
  ```bash
  cd Frontend
  npm install
  VUE_APP_API_BASE_URL=http://localhost:8002 npm run serve
  ```
  Приложение будет доступно на `http://localhost:8080`, WebSocket чат автоматом подключается к `ws://localhost:8002/ws/chat`.
- Через Docker:
  ```bash
  docker compose up --build
  ```
  (из корня проекта, поднимет `db`, `app`, `frontend`). Фронтенд доступен на `http://localhost:8080`, а сам браузер обращается к бэкенду по тому же хосту (`http://<host>:8002`) автоматически, переменные окружения не требуются.
- Интерфейс включает:
  - Чат с отображением статуса соединения и истории ответов
  - Список документов с пагинацией, поиском, скачиванием и удалением
  - Форму загрузки PDF (работает через `POST /createdoc`)
- При необходимости можно задать `VUE_APP_API_BASE_URL` перед сборкой фронтенда, но по умолчанию он ориентируется на тот же хост, с которого открыт интерфейс.

## Синхронизация рекомендаций Минздрава

- Скрипт `python -m docs_processing.upload_files` скачивает реестр, сохраняет PDF в таблицу `documents` и отправляет чанки в embedding-service.
- Управление через переменные окружения:
  - `LOAD_MINZDRAV_DATA=true` – запуск синхронизации в `python -m db.init_db`
  - `LOAD_MINZDRAV_LIMIT` – ограничение количества документов (для быстрой загрузки)
  - `LOAD_MINZDRAV_FORCE=true` – перезаписать уже существующие записи
  - `LOAD_MINZDRAV_PUSH_EMBEDDINGS=false` – загрузить только PDF без вызова embedding-service
- Параметры нарезки и отправки чанков: `PDF_CHUNK_SIZE`, `PDF_CHUNK_OVERLAP`, `PDF_MIN_CHUNK_LENGTH`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_BATCH_SIZE`.

## Загрузка клинических рекомендаций Минздрава

- Скрипт `docs_processing/upload_files.py` синхронизирует реестр клинических рекомендаций с сайта Минздрава, сохраняет PDF-документы в таблицу `documents` и отправляет чанки текста в `embedding-service`.
- Запуск вручную:
  ```bash
  python -m docs_processing.upload_files
  ```
  Дополнительные параметры задаются переменными окружения:
  - `LOAD_MINZDRAV_DATA=true` – автоматически запускать синхронизацию при `python -m db.init_db`
  - `LOAD_MINZDRAV_LIMIT=50` – ограничить количество документов (по умолчанию загружается всё)
  - `LOAD_MINZDRAV_FORCE=true` – перезаписывать уже имеющиеся документы
  - `LOAD_MINZDRAV_PUSH_EMBEDDINGS=false` – пропустить выгрузку в embedding-service
  - `PDF_CHUNK_SIZE`, `PDF_CHUNK_OVERLAP`, `PDF_MIN_CHUNK_LENGTH` – параметры нарезки текста
  - `EMBEDDING_DIMENSIONS`, `EMBEDDING_BATCH_SIZE` – параметры запроса к embedding-service
- Каждый чанк снабжается метаданными: `document_id`, `document_name`, `recommendation_number`, `page`, `chunk_id`, `source_url`, `mcb`, `age_category`, `developer`, `publish_date`. Эти метаданные сохраняются в векторной БД и используются при подборе ответов и формировании промпта для LLM, что гарантирует ответы только на основе загруженных документов.