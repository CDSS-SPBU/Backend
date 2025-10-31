from db.postgres import DataManager
from fastapi.responses import Response
from typing import List, Dict

data_base = DataManager()


class DocumentService:
    @staticmethod
    def create_doc(doc_id: str, title: str, mcb: str, age_category: str, developer: str, file_data: bytes):
        data_base.add_to_upload_list(doc_id, title, mcb, age_category, developer, data=file_data)
        data_base.upload_data()

    # @staticmethod
    # def get_all_docs():
    #     return data_base.get_all_docs()

    @staticmethod
    def get_all_docs(page: int = 0, size: int = 10) -> List[Dict]:
        return data_base.get_docs_paginated(page=page, size=size)

    @staticmethod
    def get_total_documents() -> int:
        all_docs = data_base.get_all_docs()
        return len(all_docs)

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
            return Response(
                content=ans[6],
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=document_{doc_id}.pdf"})
        return None
