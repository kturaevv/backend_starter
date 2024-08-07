from fastapi import APIRouter, WebSocket, Depends
from fastapi.responses import HTMLResponse

from src.auth.dependencies import domain_registered

router = APIRouter(prefix="/chat")


@router.get("/")
async def get(domain_supported: bool = Depends(domain_registered)):
    return HTMLResponse(open("./src/chat/index.html", "r").read())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo message: {data}")
