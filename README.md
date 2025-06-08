# Bot de Trading - Producto Mínimo Viable (MVP)

## Descripción

Bot de trading en Python para operar en Deriv usando estrategias basadas en medias móviles exponenciales (EMA) y Bandas de Bollinger.

## Estrategias Disponibles

### 1. Estrategia Clásica de Vela Contraria + Bollinger

- **Filtro de tendencia:** Usa la EMA de 200 períodos para definir si solo busca compras (tendencia alcista) o ventas (tendencia bajista).
- **Condiciones de entrada:**
  - El precio debe salir fuera de la Banda de Bollinger (Close < BB_lower para compras, Close > BB_upper para ventas).
  - Debe formarse una vela contraria que cubra más del 50% del cuerpo de la vela anterior.
  - Si se cumple, se ejecuta la entrada en la dirección de la nueva vela.

### 2. Estrategia de Rebote Técnico Dinámico en Bandas de Bollinger

- **Filtro de tendencia:** Usa la EMA de 200 períodos para definir la tendencia.
- **Condiciones de entrada:**
  - **Tendencia alcista:**  
    - Close < BB_lower  
    - EMA_5 > EMA_50  
    - (EMA_5 - Close) / Close > 0.003  
    - Señal de compra ("buy")
  - **Tendencia bajista:**  
    - Close > BB_upper  
    - EMA_5 < EMA_50  
    - (Close - EMA_5) / Close > 0.003  
    - Señal de venta ("sell")

## Selección de Estrategia

Puedes elegir la estrategia a utilizar modificando la variable `STRATEGY` en el archivo `bot.py`:

```python
STRATEGY = "classic"  # Para la estrategia clásica de vela contraria
# o
STRATEGY = "bollinger_rebound_dynamic"  # Para la estrategia de rebote técnico dinámico
```

## Instalación y ejecución

Sigue estos pasos para instalar y ejecutar el proyecto:

### 1. Clonar el repositorio

```bash
git clone https://github.com/rfconsulting/bot_trading_ec.git
cd bot_trading_ec
```

### 2. Crear un entorno virtual

```bash
python -m venv env
```

### 3. Activar el entorno virtual

En Windows:
```bash
env\Scripts\activate
```

En macOS/Linux:
```bash
source env/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Configuración de Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu token y el ID de la app siguiendo este modelo:

```properties
app_id=TU_APP_ID
token=TU_TOKEN
```

Reemplaza `TU_APP_ID` y `TU_TOKEN` con los valores correspondientes.

### 6. Ejecutar la aplicación principal

```bash
python bot.py
```

---

**Puedes modificar la estrategia en cualquier momento cambiando el valor de la variable `STRATEGY` en `bot.py`.**