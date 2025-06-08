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