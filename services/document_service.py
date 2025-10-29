from db.postgres import DataManager

data_base = DataManager()


class DocumentService:
    @staticmethod
    def create_doc(doc_id: str, title: str, file_data: bytes):
        data_base.add_to_upload_list(doc_id, title, data=file_data)
        data_base.upload_data()

    @staticmethod
    def get_all_docs():
        return data_base.get_all_docs()

    @staticmethod
    def delete_doc(doc_id: str) -> bool:
        ans = data_base.is_doc_exist(doc_id)
        if ans:
            data_base.delete_data((doc_id,))
            return True
        return False

    @staticmethod
    def get_doc(doc_id: str):
        ans = data_base.is_doc_exist(doc_id)
        if ans:
            doc_data = {
                'id_cr': ans[0],
                'title': ans[1],
                'MCB': ans[2],
                'age_category': ans[3],
                'developer': ans[4],
                'placement_date': ans[5].isoformat() if ans[5] else None
            }
            return doc_data
        return None
