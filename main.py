from fastapi import FastAPI
from api.router_socket import socket_router
from api.router_page import page_router
from docs_processing.upload_files import minzdrav_excel


app = FastAPI(title="Medical Support")
app.include_router(socket_router)
app.include_router(page_router)

# создание базы данных
# minzdrav_excel()
