import datetime
import psycopg2
from psycopg2.extras import execute_values


class DataManager:
    def __init__(self):
        self.upload_list = []

    def create_table(self):
        conn = psycopg2.connect(
            dbname="clinical_recommendations",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                id_cr VARCHAR(10) PRIMARY KEY NOT NULL UNIQUE,
                title VARCHAR(400) NOT NULL,
                MCB VARCHAR(400),
                age_category VARCHAR(20) NOT NULL,
                developer VARCHAR(1000),
                placement_date DATE,
                data BYTEA NOT NULL
                );
            ''')

        cur.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'documents'
              AND constraint_name = 'chk_documents_age';
        """)

        if cur.fetchone() is None:
            cur.execute("""
                ALTER TABLE documents
                ADD CONSTRAINT chk_documents_age CHECK (
                    age_category IN ('Взрослые', 'Дети', 'Взрослые, дети')
                );
            """)
        cur.close()
        conn.close()

    def creation_db(self) -> bool:
        is_already_created = False
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )

        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""SELECT 1 FROM pg_database WHERE datname = 'clinical_recommendations';""")

        if cur.fetchone() is None:
            cur.execute("CREATE DATABASE clinical_recommendations;")
            self.create_table()
            is_already_created = True

        cur.close()
        conn.close()
        return is_already_created

    def add_to_upload_list(self, id_cr, title, MCB="NULL", age_category='Взрослые', developer='NULL',
                           placement_date=datetime.date.today(), data='NULL'):
        self.upload_list.append((id_cr, title, MCB, age_category, developer, placement_date, data))

    def upload_data(self):
        conn = psycopg2.connect(
            dbname="clinical_recommendations",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()
        execute_values(cur, """
            INSERT INTO documents (id_cr, title, MCB, age_category, developer, placement_date, data)
            VALUES %s""", self.upload_list)

        cur.close()
        conn.close()

        self.upload_list = []

    def delete_data(self, tpl):
        conn = psycopg2.connect(
            dbname="clinical_recommendations",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()

        query = f"DELETE FROM documents WHERE id_cr IN %s"
        cur.execute(query, tpl)

        cur.close()
        conn.close()

    def is_doc_exist(self, doc_id):
        conn = psycopg2.connect(
            dbname="clinical_recommendations",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )

        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"""SELECT * FROM documents WHERE id_cr = '{doc_id}';""")
        ans = cur.fetchone()

        cur.close()
        conn.close()
        return ans

    def get_all_docs(self):
        conn = psycopg2.connect(
            dbname="clinical_recommendations",
            user="postgres",
            password="qwerty",
            host="localhost",
            port="5432"
        )

        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"""SELECT id_cr, title, MCB, age_category, developer, placement_date FROM documents;""")
        ans = cur.fetchall()

        cur.close()
        conn.close()
        return ans
