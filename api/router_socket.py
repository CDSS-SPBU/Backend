import fastapi
import json
import requests
from fastapi import WebSocket, WebSocketDisconnect
from services.chat_service import ChatSessionManager

socket_router = fastapi.APIRouter()
session_manager = ChatSessionManager()

EMBEDDING_SERVICE_URL = "http://localhost:8000/embed"


@socket_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = None

    try:
        session_id = session_manager.create_session()
        await websocket.send_text(json.dumps({"type": "session_created", "session_id": session_id}, ensure_ascii=False))

        history = session_manager.get_history(session_id)
        await websocket.send_text(json.dumps({"type": "history", "messages": history}, ensure_ascii=False))

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "chat_message":
                    user_query = msg.get("query", "").strip()
                    if not user_query:
                        continue

                    session_manager.add_message(session_id, "user", user_query)

                    # работа с моделью
                    response = get_response(user_query)

                    # response = f"Ваш запрос: {user_query}. Ожидайте ответа из клинических рекомендаций."
                    session_manager.add_message(session_id, "bot", response)

                    await websocket.send_text(
                        json.dumps({"type": "chat_message", "role": "bot", "content": response}, ensure_ascii=False))

                if msg.get("type") == "history":
                    history = session_manager.get_history(session_id)
                    await websocket.send_text(json.dumps({"type": "history", "messages": history}, ensure_ascii=False))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": e}, ensure_ascii=False))
    except WebSocketDisconnect:
        session_manager.remove_session(session_id)


def get_response(user_query):
    try:
        embed_request = {
            "text": [user_query],
            "task": "retrival.query",
            "dimension": 1024
        }
        response = requests.post(EMBEDDING_SERVICE_URL, json=embed_request)
        response.raise_for_status()
        embedding_data = response.json()

        embedding = embedding_data["embedding"][0]

        response_text = f"Эмбеддинг получен. Размер: {len(embedding)}"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при вызове embedding-service: {e}")
        response_text = "Ошибка при генерации эмбеддинга"
    except Exception as e:
        print(f"Ошибка обработки эмбеддинга: {e}")
        response_text = "Ошибка обработки"
    return response_text
