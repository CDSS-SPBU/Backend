import time
from postgres import DataManager


def initialize_database():
    print("Инициализация базы данных...")

    data_manager = DataManager()

    try:
        data_manager.initialization_db()
        print("База данных успешно инициализирована")

        # Опционально: загрузка начальных данных
        from docs_processing.upload_files import minzdrav_excel
        # print("Загрузка начальных данных...")
        minzdrav_excel()

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        # Повторная попытка через 5 секунд
        time.sleep(5)
        initialize_database()


if __name__ == "__main__":
    initialize_database()