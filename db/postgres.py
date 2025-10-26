import psycopg2


def creation_db() -> bool:
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
        create_table()
        is_already_created = True

    cur.close()
    conn.close()
    return is_already_created


def create_table():
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
            id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            id_cr VARCHAR(10) NOT NULL UNIQUE,
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


creation_db()
