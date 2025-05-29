


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
