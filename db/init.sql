CREATE TABLE IF NOT EXISTS documents (
    id_cr VARCHAR(10) PRIMARY KEY NOT NULL UNIQUE,
    title VARCHAR(400) NOT NULL,
    MCB VARCHAR(400),
    age_category VARCHAR(20) NOT NULL,
    developer VARCHAR(1000),
    placement_date DATE,
    data BYTEA NOT NULL
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'documents'
          AND constraint_name = 'chk_documents_age'
    ) THEN
        ALTER TABLE documents
        ADD CONSTRAINT chk_documents_age CHECK (
            age_category IN ('Взрослые', 'Дети', 'Взрослые, дети')
        );
    END IF;
END
$$;