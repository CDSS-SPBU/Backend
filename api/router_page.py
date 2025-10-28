from fastapi import APIRouter, HTTPException
from services.document_service import DocumentService


page_router = APIRouter()


@page_router.get("/")
async def root():
    return {
        "status": "ok",
        "message": "WebSocket чат доступен по /ws/chat"
    }


@page_router.get("/doclist")  # получение всех документов
async def get_docs():
    return DocumentService.get_all_docs()


@page_router.delete("/doclist/{doc_id}")  # удаление документа по id
async def delete_doc(doc_id: str):
    DocumentService.delete_doc(doc_id)


@page_router.get("/doclist/{doc_id}")  # скачивание документа по id
async def get_doc_id(doc_id: str):
    document = DocumentService.get_doc(doc_id)
    if document:
        return document
    raise HTTPException(status_code=404, detail="Файл не найден")


@page_router.post("/createdoc")  # загрузка нового документа
async def upload_doc(doc_id: str, title: str, file_data: bytes):
    document = DocumentService.create_doc(doc_id, title, file_data)
    if not document:
        raise HTTPException(status_code=409, detail="Файл с таким названием уже существует")
