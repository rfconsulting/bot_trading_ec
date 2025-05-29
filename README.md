# Bot de Trading - Producto Mínimo Viable (MVP)

## Descripción

Bot de trading en Python basado en la siguiente estrategia para usar con datos de trading (operando en la plataforma Deriv):

- Utiliza tres medias móviles exponenciales (EMA):
  - EMA de 200 períodos (tendencia general)
  - EMA de 50 períodos
  - EMA de 5 períodos
- Añade una Banda de Bollinger con los parámetros estándar (20 períodos, 2 desviaciones estándar).

### Condiciones de entrada a una operación

- El precio debe salir fuera de la Banda de Bollinger.
- Luego debe formarse una vela contraria que cubra más del 50% del cuerpo de la vela anterior (ejemplo: si la vela anterior fue bajista, se necesita una vela alcista que cubra más del 50% de su cuerpo).
- Si se cumple, se ejecuta la entrada en la dirección de la nueva vela.
- La reentrada se hace cada vez que se repite la condición anterior.


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
