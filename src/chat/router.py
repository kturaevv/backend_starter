from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/chat")


@router.get("/")
async def get():
    return HTMLResponse(open("./src/chat/index.html", "r").read())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo message: {data}")
