import pandas as pd
import ta


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