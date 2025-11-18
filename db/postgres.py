import datetime
import psycopg2
import logging
import os, time
from psycopg2.extras import execute_values, RealDictCursor
from typing import Tuple

logger = logging.getLogger(__name__)


class DataConnection:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME", "clinical_recommendations")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "qwerty")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")


class DataManager:
    def __init__(self):
        self.connection = DataConnection()
        self.upload_list = []

    def _get_connection(self, dbname):
        conn_config = {
            'dbname': dbname or self.connection.dbname,
            'user': self.connection.user,
            'password': self.connection.password,
            'host': self.connection.host,
            'port': self.connection.port
        }
        return psycopg2.connect(**conn_config)

    def wait_for_db(self, max_retries=30, delay=2):
        """Ожидание готовности базы данных"""
        for i in range(max_retries):
            try:
                conn = self._get_connection("postgres")
                conn.close()
                logger.info("База данных готова")
                return True
            except psycopg2.OperationalError as e:
                logger.warning(f"Попытка {i+1}/{max_retries}: База данных не готова, ждем...")
                time.sleep(delay)
        raise Exception("Не удалось подключиться к базе данных")

    def create_database(self):
        """Создание базы данных если не существует"""
        try:
            conn = self._get_connection("postgres")
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.connection.dbname}'")
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f"CREATE DATABASE {self.connection.dbname}")
                    logger.info(f"База данных {self.connection.dbname} создана")
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка при создании базы данных: {e}")
            raise

    def create_table(self):
        create_query = '''
            CREATE TABLE IF NOT EXISTS documents (
            id_cr VARCHAR(10) PRIMARY KEY NOT NULL UNIQUE,
            title VARCHAR(400) NOT NULL,
            MCB VARCHAR(400),
            age_category VARCHAR(20) NOT NULL,
            developer VARCHAR(1000),
            placement_date DATE,
            data BYTEA NOT NULL
            );
        '''

        check_constraint_query = """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'documents'
              AND constraint_name = 'chk_documents_age';
        """

        add_constraint_query = """
            ALTER TABLE documents
            ADD CONSTRAINT chk_documents_age CHECK (
                age_category IN ('Взрослые', 'Дети', 'Взрослые, дети')
            );
        """

        self._execute_query(create_query)
        if not self._execute_query(check_constraint_query, fetch=True):
            self._execute_query(add_constraint_query)
        logger.info("Таблица documents создана/проверена")

    def initialization_db(self):
        """Полная инициализация базы данных"""
        self.wait_for_db()
        self.create_database()
        self.create_table()

    def _execute_query(self, query: str, params: Tuple = None, dbname: str = None, fetch: bool = False):
        try:
            with self._get_connection(dbname) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if fetch:
                        return cur.fetchall()
                    return cur
        except psycopg2.Error as e:
            logger.error(f"Ошибка в базе данных: {e}")
            raise

    def add_to_upload_list(self, id_cr, title, MCB="NULL", age_category='Взрослые', developer='NULL',
                           placement_date=datetime.date.today(), data='NULL'):
        self.upload_list.append((id_cr, title, MCB, age_category, developer, placement_date, data))

    def upload_data(self):
        insert_query = """ INSERT INTO documents (id_cr, title, MCB, age_category, developer, placement_date, data)
            VALUES %s"""

        try:
            with self._get_connection(dbname=self.connection.dbname) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    execute_values(cur, insert_query, self.upload_list)
            self.upload_list = []
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            raise

    def delete_data(self, tpl):
        delete_query = "DELETE FROM documents WHERE id_cr IN %s"

        try:
            with self._get_connection(dbname=self.connection.dbname) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(delete_query, (tpl,))

        except Exception as e:
            logger.error(f"Ошибка при удалении документов: {e}")
            raise

    def is_doc_exist(self, doc_id):
        query = """SELECT id_cr, title, MCB, age_category, developer, placement_date, data FROM documents
        WHERE id_cr = %s;"""

        try:
            with self._get_connection(dbname=self.connection.dbname) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(query, (doc_id,))
                    ans = cur.fetchone()
                    return ans
        except Exception as e:
            logger.error(f"Ошибка получения файла: {e}")
            return []

    def get_all_docs(self):
        query = """SELECT id_cr, title, MCB, age_category, developer, placement_date FROM documents;"""

        try:
            with self._get_connection(dbname=self.connection.dbname) as conn:
                conn.autocommit = True
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    ans = cur.fetchall()
                    return [dict(row) for row in ans]
        except Exception as e:
            logger.error(f"Ошибка получения всех файлов: {e}")
            return []

    def get_docs_paginated(self, page: int = 0, size: int = 10):
        query = """
            SELECT id_cr, title, MCB, age_category, developer, placement_date 
            FROM documents 
            ORDER BY id_cr
            LIMIT %s OFFSET %s;
        """

        try:
            with self._get_connection(dbname=self.connection.dbname) as conn:
                conn.autocommit = True
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (size, page * size))
                    ans = cur.fetchall()
                    return [dict(row) for row in ans]
        except Exception as e:
            logger.error(f"Ошибка получения файлов с пагинацией: {e}")
            return []
