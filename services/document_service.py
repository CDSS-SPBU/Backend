# временная мера
DOCUMENTS = {"1": {"doc_id": "id1", "title": "t1", "file_data": "book1"},
             "2": {"doc_id": "id2", "title": "t2", "file_data": "book2"},
             "3": {"doc_id": "id3", "title": "t3", "file_data": "book3"}}


class DocumentService:
    @staticmethod
    def create_doc(doc_id: str, title: str, file_data: str) -> bool:
        if doc_id not in DOCUMENTS:
            DOCUMENTS[doc_id] = {"doc_id": doc_id, "title": title, "file_data": file_data}
            return True
        return False

    @staticmethod
    def get_all_docs():
        return DOCUMENTS

    @staticmethod
    def delete_doc(doc_id: str) -> bool:
        if doc_id in DOCUMENTS:
            del DOCUMENTS[doc_id]
            return True
        return False

    @staticmethod
    def get_doc(doc_id: str):
        if doc_id in DOCUMENTS:
            return DOCUMENTS[doc_id]
