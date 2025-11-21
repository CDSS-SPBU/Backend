from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Query
from services.document_service import DocumentService
from docs_processing.pageable import Pageable, PaginatedResponse


page_router = APIRouter()


@page_router.get("/")
async def root():
    return {
        "status": "ok",
        "message": "WebSocket чат доступен по /ws/chat"
    }


# @page_router.get("/doclist")  # получение всех документов
# async def get_docs():
#     return DocumentService.get_all_docs()


@page_router.get("/doclist/paginated")  # получение всех документов с пагинацией
async def get_docs_paginated(
        page: int = Query(0, ge=0, description="Номер страницы (начинается с 0)"),
        size: int = Query(10, ge=1, le=100, description="Размер страницы (1-100)"),
        search: str | None = Query(None, max_length=255, description="Поиск по ID или названию")
):
    search_value = search.strip() if search else None
    docs = DocumentService.get_all_docs(page=page, size=size, search=search_value)
    total = DocumentService.get_total_documents(search=search_value)

    return PaginatedResponse(
        items=docs,
        total=total,
        pageable=Pageable(page=page, size=size),
        total_pages=(total + size - 1) // size
    )


@page_router.delete("/doclist/{doc_id}")  # удаление документа по id
async def delete_doc(doc_id: str):
    if not DocumentService.delete_doc(doc_id):
        raise HTTPException(status_code=404, detail="Файл для удаления не найден")


@page_router.get("/doclist/{doc_id}")  # скачивание документа по id
async def get_doc_id(doc_id: str):
    document = DocumentService.get_doc(doc_id)
    if document:
        return document
    raise HTTPException(status_code=404, detail="Файл не найден")


@page_router.post("/createdoc")  # загрузка нового документа
async def upload_doc(doc_id: str = Form(..., description="ID документа"),
                     title: str = Form(..., description="Навзвание документа"),
                     mcb: str = Form("NULL", description="МКБ-10"),
                     age_category: str = Form("Взрослые", description="Возрастная категория"),
                     developer: str = Form("NULL", description="Разработчик"),
                     file: UploadFile = File(..., description="PDF файл")):

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Неправильный формат файла")

    # пока не проверяем существует ли уже такой id и просто перезаписываем
    # if DocumentService.get_doc(doc_id):
    #     raise HTTPException(status_code=409, detail="Файл с таким названием уже существует")

    file_data = await file.read()
    try:
        DocumentService.create_doc(doc_id, title, mcb, age_category, developer, file_data)
        return {
            "message": "Новый документ загружен",
            "doc_id": doc_id,
            "title": title,
            "MCB": mcb,
            "age_category": age_category,
            "developer": developer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в загрузке документе: {str(e)}")
