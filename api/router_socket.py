import fastapi
import json
from fastapi import WebSocket, WebSocketDisconnect
from services.chat_service import ChatSessionManager

socket_router = fastapi.APIRouter()
session_manager = ChatSessionManager()


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
                    response = f"Ваш запрос: {user_query}. Ожидайте ответа из клинических рекомендаций."
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
