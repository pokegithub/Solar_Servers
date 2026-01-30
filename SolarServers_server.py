import asyncio
import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Body

from SolarServers_core import SolarServerCore

app = FastAPI()
core = SolarServerCore()

INTERVAL = 0.25

@app.on_event("startup")
async def on_startup():
    print("SolarServers server online")
    print(f"Admin mode: {core.meta.get('is_admin', False)}")

@app.on_event("shutdown")
async def on_shutdown():
    print("SolarServers server shutting")

@app.websocket("/ws")
async def websocket_stream(ws: WebSocket):
    await ws.accept()
    print("WebSocket client connected")
    try:
        while True:
            packet = core.get_packet()
            await ws.send_json(packet)
            await asyncio.sleep(INTERVAL)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"Error: {e}")

@app.post("/kill")
def kill_process(pid: int = Body(..., embed = True)):
    if not core.meta.get("is_admin", False):
        return {"error": "Permissions not sufficient"}
    try:
        process = psutil.Process(pid)
        process.terminate()
        return {"status": "Terminated", "pid": pid}
    except psutil.NoSuchProcess:
        return {"error": "Process not found"}
    except Exception as e:
        return {"error": str(e)}