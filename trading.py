import os
import json
import websockets



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