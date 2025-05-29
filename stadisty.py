import os
import pandas as pd
import csv
from datetime import datetime


CSV_FILE = "historico_ticks_con_indicadores.csv"
CSV_FILE_BACKUP = "historico_ticks_con_indicadores_backup.csv"
LOG_FILE = "operaciones_log.csv"


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