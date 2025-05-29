import os
import json
import websockets
from dotenv import load_dotenv



load_dotenv()
app_id = os.getenv("app_id")
token = os.getenv("token")

CSV_FILE = "historico_ticks_con_indicadores.csv"
LOG_FILE = "operaciones_log.csv"

async def connect_ws():
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={app_id}"
    ws = await websockets.connect(uri)
    await ws.send(json.dumps({"authorize": token}))
    auth = json.loads(await ws.recv())
    if auth.get("msg_type") != "authorize":
        raise Exception("No autorizado en Deriv WebSocket")
    print("Conexión WebSocket establecida")
    return ws


async def close_ws(ws):
    if ws:
        await ws.close()