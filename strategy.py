


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


def check_entry_bollinger_rebound(df):
    """
    Estrategia de rebote técnico en Bandas de Bollinger con filtro de tendencia y sobreventa.
    Solo busca compras.
    """
    if len(df) < 3:
        return None

    last = df.iloc[-1]
    # Condición 1: Close < BB_lower
    if last["Close"] < last["BB_lower"]:
        # Condición 2: EMA_5 > EMA_50
        if last["EMA_5"] > last["EMA_50"]:
            # Condición 3: (EMA_5 - Close) / Close > 0.003
            if (last["EMA_5"] - last["Close"]) / last["Close"] > 0.003:
                print("Señal de compra por rebote técnico Bollinger")
                return "buy"
    return None


def check_entry_bollinger_rebound_dynamic(df):
    """
    Estrategia de rebote técnico en Bandas de Bollinger con filtro de tendencia (EMA 200).
    - Si tendencia es alcista (bull), busca rebotes de compra.
    - Si tendencia es bajista (bear), busca rebotes de venta.
    """
    if len(df) < 3:
        return None

    last = df.iloc[-1]
    trend = "bull" if last["EMA_200"] < last["Close"] else "bear"

    if trend == "bull":
        # Señal de compra
        if last["Close"] < last["BB_lower"]:
            if last["EMA_5"] > last["EMA_50"]:
                if (last["EMA_5"] - last["Close"]) / last["Close"] > 0.003:
                    print("Señal de COMPRA por rebote técnico Bollinger (tendencia alcista)")
                    return "buy"
    else:
        # Señal de venta
        if last["Close"] > last["BB_upper"]:
            if last["EMA_5"] < last["EMA_50"]:
                if (last["Close"] - last["EMA_5"]) / last["Close"] > 0.003:
                    print("Señal de VENTA por rebote técnico Bollinger (tendencia bajista)")
                    return "sell"
    return None