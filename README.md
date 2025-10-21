Струткура проекта

medical_support_project/\
├── docs_processing/           # Первичная обработка документов\
|   ├── upload_files.py        # Загрузка документов с сайта клинических рекомендаций\
|   ├── pdf_parser.py          # Парсер документов\
|   └── text_cleaner.py        # Исправление ошибок\
├── static/                    # Загруженные PDF\
├── db/                        # Работа с БД\
│   ├── postgres.py            # Хранение исходных документов\
│   └── vector_db.py           # Qdrant/Weaviate/Chroma\
├── api/                       # Директория с API-роутами\
│   ├── router_page.py         # Роуты для страниц\
│   └── router_socket.py       # Роуты для WebSocket-соединений\
├── services/                  # Основные взаимодействия с пользователем\
|   ├── chat_service.py\
│   └── document_service.py\
├── requirements.txt           # Файл зависимостей проекта\
├── .env                       # Переменные окружения\
└── main.py                    # Запуск приложения\
