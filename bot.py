import json
from datetime import datetime
import asyncio
import pandas as pd
from connect_ws import connect_ws, close_ws
from indicators import calculate_indicators
from data import download_and_update_data, update_with_latest_data
from trading import place_trade, check_entry
from stadisty import log_trade, calcular_efectividad, CSV_FILE


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
