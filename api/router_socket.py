import fastapi
import json
import requests
import httpx, logging, asyncio, asyncpg
from fastapi import WebSocket, WebSocketDisconnect
from services.chat_service import ChatSessionManager

socket_router = fastapi.APIRouter()
session_manager = ChatSessionManager()

logger = logging.getLogger("example")
# сделать через env
EMBEDDING_SERVICE_URL = "http://localhost:8000/embed"
RERANK_SERVICE_URL = "http://localhost:8001/rerank"


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


async def get_response(user_query: str) -> str:
    # получение эмбеддинга
    try:
        async with httpx.AsyncClient() as client:  # ассинхронный клиент, не блокирует событийный цикл
            embed_request = {
                "texts": [user_query],
                "metadata": [{}],
                "task": "retrieval.query",
                "dimensions": 1024
            }
            response = await client.post(EMBEDDING_SERVICE_URL, json=embed_request, timeout=30.0)
            response.raise_for_status()
            embedding_data = response.json()
            embedding = embedding_data["embedding"][0]
            # NOTE: убрать
            print(len(embedding))
            logger.info(f"Эмбеддинг получен. Размер: {len(embedding)}")
    except Exception as e:
        logger.error(f"Ошибка при генерации эмбеддинга: {e}")

    # db retrieval
    try:
        # Database connection parameters
        conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            database='rag',
            user='dev',
            password='dev_password'
        )

        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        # Query to find similar embeddings using cosine similarity
        query = """
            SELECT id, content, metadata->>'document_name' as document_name, metadata->>'source_url' as source_url,
                   1-(embedding <=> $1::vector) as similarity
            FROM chunks
            ORDER BY similarity DESC
            LIMIT 3;
        """

        # Execute query with the generated embedding
        db_results = await conn.fetch(query, embedding_str)
        texts_for_rerank = [record['content'] for record in db_results]

        print(texts_for_rerank)
        # Close the connection
        await conn.close()

        # Log and return results
        logger.info(f"Found {len(db_results)} similar embeddings")

    except asyncpg.PostgresError as e:
        logger.error(f"Database error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during database query: {e}")
        return None

    # rerank
    try:
        async with httpx.AsyncClient() as client:  # ассинхронный клиент, не блокирует событийный цикл
            rerank_request = {
                "query": user_query,
                "passages": texts_for_rerank,
            }
            response = await client.post(RERANK_SERVICE_URL, json=rerank_request, timeout=30.0)
            response.raise_for_status()
            rerank_data = response.json()

            # NOTE: убрать
            logger.info("Rerank получен")
            return rerank_data
    except Exception as e:
        logger.error(f"Ошибка при rerank: {e}")