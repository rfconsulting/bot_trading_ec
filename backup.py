import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import pandas as pd
import ta
from datetime import datetime
import csv

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


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EMA_5"] = ta.trend.EMAIndicator(df["Close"], window=5).ema_indicator()
    df["EMA_50"] = ta.trend.EMAIndicator(df["Close"], window=50).ema_indicator()
    df["EMA_200"] = ta.trend.EMAIndicator(df["Close"], window=200).ema_indicator()
    bb = ta.volatility.BollingerBands(df["Close"], window=20, window_dev=2)
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    df["BB_middle"] = bb.bollinger_mavg()
    return df


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

def check_entry(df):
    """
    Filtra primero por tendencia (EMA 200):
    - Si tendencia es bull, solo busca señales de compra.
    - Si tendencia es bear, solo busca señales de venta.
    Luego aplica la estrategia de entrada.
    """
    if len(df) < 3:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]
    trend = "bull" if last["EMA_200"] < last["Close"] else "bear"


    if trend == "bull":
        print("Tendencia actual: \033[92m↑ Alcista\033[0m")  # Verde
        # Solo buscar señales de compra
        if last["Close"] < last["BB_lower"]:
            if prev["Close"] > prev["Open"]:
                body_prev = abs(prev["Close"] - prev["Open"])
                body_last = abs(last["Close"] - last["Open"])
                if body_last > 0.5 * body_prev:
                    return "buy"
    elif trend == "bear":
        print("Tendencia actual: \033[91m↓ Bajista\033[0m")  # Rojo
        # Solo buscar señales de venta
        if last["Close"] > last["BB_upper"]:
            if prev["Close"] < prev["Open"]:
                body_prev = abs(prev["Close"] - prev["Open"])
                body_last = abs(last["Close"] - last["Open"])
                if body_last > 0.5 * body_prev:
                    return "sell"
    return None

async def place_trade(ws, symbol, action, stake):
    try:
        proposal = {
            "buy": 1,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "CALL" if action == "buy" else "PUT",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": symbol
            },
            "passthrough": {"bot": "ema_bollinger"}
        }
        await ws.send(json.dumps({"proposal": proposal["parameters"]}))
        response = json.loads(await ws.recv())

        if "error" in response:
            print(f"❌ Error en la propuesta: {response['error'].get('message', response['error'])}")
            return response

        if "proposal" in response:
            buy_req = {
                "buy": response["proposal"]["id"],
                "price": stake
            }
            await ws.send(json.dumps(buy_req))
            buy_res = json.loads(await ws.recv())
            if "error" in buy_res:
                print(f"❌ Error al ejecutar la compra: {buy_res['error'].get('message', buy_res['error'])}")
            else:
                print("✔️ Operación ejecutada:", buy_res)
            return buy_res
        else:
            print("❌ Respuesta inesperada al solicitar la propuesta:", response)
            return response
    except Exception as e:
        print(f"❌ Excepción en place_trade: {e}")
        return {"error": str(e)}
    

def log_trade(fecha, tipo, monto, tiempo, resultado, efectividad):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Fecha", "Tipo", "Monto", "Tiempo", "Resultado", "Efectividad"])
        writer.writerow([fecha, tipo, monto, tiempo, resultado, f"{efectividad:.2f}%"])

def calcular_efectividad():
    if not os.path.isfile(LOG_FILE):
        return 0.0
    df = pd.read_csv(LOG_FILE)
    if len(df) == 0:
        return 0.0
    ganadas = df[df["Resultado"] == "GANADA"].shape[0]
    return (ganadas / len(df)) * 100


async def main():
    await download_and_update_data()  # Solo una vez al inicio
    while True:
        try:
            await update_with_latest_data()
            print("📊 Datos descargados y actualizados.")
            df = pd.read_csv(CSV_FILE, parse_dates=["Time"])
            signal = check_entry(df)
            if signal:
                ws = await connect_ws()
                try:
                    trade_result = await place_trade(ws, "R_100", signal, 1.0)
                    # Esperar resultado final del contrato
                    if "buy" in trade_result and "contract_id" in trade_result["buy"]:
                        contract_id = trade_result["buy"]["contract_id"]
                        # Espera el cierre del contrato
                        while True:
                            await ws.send(json.dumps({"proposal_open_contract": 1, "contract_id": contract_id}))
                            status = json.loads(await ws.recv())
                            if status.get("proposal_open_contract", {}).get("is_sold"):
                                profit = status["proposal_open_contract"]["profit"]
                                resultado = "GANADA" if profit > 0 else "PERDIDA"
                                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                efectividad = calcular_efectividad()
                                log_trade(
                                    fecha=fecha,
                                    tipo=signal,
                                    monto=1.0,
                                    tiempo=status["proposal_open_contract"]["date_expiry"],
                                    resultado=resultado,
                                    efectividad=efectividad
                                )
                                print(f"Resultado operación: {resultado}, Ganancia: {profit}")
                                break
                            await asyncio.sleep(2)
                finally:
                    await close_ws(ws)
            else:
                print("No hay señal de entrada en esta vela.")
            await asyncio.sleep(60)
        except Exception as e:
            print(f"❌ Excepción en la iteración principal: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
    print("📈 Proceso completado")
