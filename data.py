import os
import json
import websockets
from connect_ws import connect_ws, close_ws
import pandas as pd
from indicators import calculate_indicators

CSV_FILE = "historico_ticks_con_indicadores.csv"


async def fetch_candlestick_batch(symbol, granularity, count, end_epoch):
    websocket = await connect_ws()
    try:
        request = {
            "ticks_history": symbol,
            "style": "candles",
            "granularity": granularity,
            "count": count,
            "end": end_epoch
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        data = json.loads(response)
        if "candles" not in data:
            raise ValueError("La respuesta no contiene datos de velas")
        candles = data["candles"]
        df = pd.DataFrame(candles)
        df["Time"] = pd.to_datetime(df["epoch"], unit="s")
        if "volume" not in df.columns:
            df["volume"] = 0
        df = df[["Time", "open", "high", "low", "close", "volume"]]
        df.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
        return df
    finally:
        await close_ws(websocket)

async def download_and_update_data(symbol="R_100", count=5000, granularity=60):
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE, parse_dates=["Time"])
        oldest_time = int(df_existing["Time"].min().timestamp())
        print(f"Descargando datos previos a {df_existing['Time'].min()}")
    else:
        df_existing = pd.DataFrame()
        oldest_time = int(pd.Timestamp.now().timestamp())
        print("Descargando histórico inicial...")

    df_new = await fetch_candlestick_batch(symbol, granularity, count, oldest_time)

    if df_existing.empty:
        df_total = df_new
    else:
        df_total = pd.concat([df_new, df_existing], ignore_index=True)
        df_total.drop_duplicates(subset=["Time"], inplace=True)
        df_total.sort_values("Time", inplace=True)

    df_total = calculate_indicators(df_total)
    df_total.to_csv(CSV_FILE, index=False)
    print("✔️ Archivo actualizado con nuevos datos e indicadores.")


async def update_with_latest_data(symbol="R_100", granularity=60):
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE, parse_dates=["Time"])
        last_time = int(df_existing["Time"].max().timestamp())
        # Descarga solo desde el último registro guardado hasta ahora
        now = int(pd.Timestamp.now().timestamp())
        df_new = await fetch_candlestick_batch(symbol, granularity, 10, now)
        # Filtra solo los datos más nuevos
        df_new = df_new[df_new["Time"] > df_existing["Time"].max()]
        if not df_new.empty:
            df_total = pd.concat([df_existing, df_new], ignore_index=True)
            df_total.drop_duplicates(subset=["Time"], inplace=True)
            df_total.sort_values("Time", inplace=True)
            df_total = calculate_indicators(df_total)
            df_total.to_csv(CSV_FILE, index=False)
            print("✔️ CSV actualizado con los datos más recientes.")
        else:
            print("No hay nuevos datos para agregar.")
    else:
        await download_and_update_data(symbol=symbol, count=5000, granularity=granularity)
