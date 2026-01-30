import asyncio
import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Body
from SolarServers_core import SolarServersCore

app = FastAPI()
core = SolarServersCore()

INTERVAL = 0.2

@app.on_event("startup")
async def on_startup():
    print("SolarServers server online")
    print(f"Admin mode: {core.meta.get('is_admin', False)}")

@app.on_event("shutdown")
async def on_shutdown():
    print("SolarServers server shutting")

@app.get("/")
def root():
    return {"status": "Server alive"}

@app.websocket("/ws")
async def websocket_stream(ws: WebSocket):
    await ws.accept()
    print("WS client connected")

    try:
        while True:
            try:
                packet = core.get_packet()
                await ws.send_json(packet)
                print(f"Sent packet with {len(packet['connections'])} connections")
            except Exception as e:
                print("Error scanning core:", e)
                await ws.send_json({"meta": core.meta, "connections": []})

            await asyncio.sleep(INTERVAL)
    except WebSocketDisconnect:
        print("WS client disconnected")
    except Exception as e:
        print("Error:", e)


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
