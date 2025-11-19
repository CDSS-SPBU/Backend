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