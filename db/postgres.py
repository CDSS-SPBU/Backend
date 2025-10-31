import datetime
import psycopg2
import logging
from psycopg2.extras import execute_values, RealDictCursor
from typing import Tuple

logger = logging.getLogger(__name__)


class DataConnection:
    def __init__(self):
        self.dbname = "clinical_recommendations"
        self.user = "postgres"
        self.password = "qwerty"
        self.host = "localhost"
        self.port = "5432"


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

    def creation_db(self) -> bool:
        check_db_query = """SELECT 1 FROM pg_database WHERE datname = 'clinical_recommendations';"""

        try:
            is_already_created = self._execute_query(check_db_query, (self.connection.dbname,), dbname="postgres",
                                                     fetch=True)
            if not is_already_created:
                '''CREATE DATABASE не может выполняться внутри блока транзакции
                надеемся, что бд уже создана'''
                # self._execute_query("CREATE DATABASE clinical_recommendations;", dbname="postgres")
                self.create_table()
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при создании базы данных: {e}")
            return False

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
