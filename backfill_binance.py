import os
import requests
from datetime import datetime
from collections import OrderedDict
from supabase import create_client, Client

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_p2p_history():
    """Obtiene el historial de p2pvenezuela y devuelve {fecha: primer_precio_del_dia}."""
    api_url = "https://www.p2pvenezuela.com/api/p2p/historial/90?pair=VES&t=1777844455169"
    
    print(f"Consultando {api_url} ...")
    resp = requests.get(api_url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(f"Se recibieron {len(data)} registros en total.")

    daily_first = OrderedDict()
    for entry in data:
        precio_str = entry.get("precio")
        created_at_str = entry.get("created_at")
        if not precio_str or not created_at_str:
            continue
        try:
            dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            fecha = dt.strftime("%Y-%m-%d")
            precio = float(precio_str)
        except (ValueError, TypeError):
            continue
        if fecha not in daily_first:
            daily_first[fecha] = precio

    print(f"Primeros precios de {len(daily_first)} días distintos.")
    return daily_first

def get_existing_bcv(dates):
    """
    Recupera la tasa_bcv de los registros que ya existen en Supabase para las fechas dadas.
    Retorna un dict {fecha: tasa_bcv} (solo para los que tengan valor no nulo).
    """
    if not dates:
        return {}
    # Consultar en lote: Supabase permite filtrar por lista con 'in'
    # pero tenemos que hacerlo en paginación o si son muchos días, podemos consultar rango.
    min_date = min(dates)
    max_date = max(dates)
    print(f"Consultando registros existentes entre {min_date} y {max_date}...")
    resp = supabase.table("exchange_rates") \
        .select("date, tasa_bcv") \
        .gte("date", min_date) \
        .lte("date", max_date) \
        .execute()
    existing = {}
    if resp.data:
        for row in resp.data:
            if row["tasa_bcv"] is not None:
                existing[row["date"]] = row["tasa_bcv"]
    print(f"Se encontraron {len(existing)} registros con tasa_bcv ya guardada.")
    return existing

def save_rows(daily_prices):
    """Inserta/actualiza solo la tasa_binance, respetando la tasa_bcv existente."""
    if not daily_prices:
        print("No hay datos para guardar.")
        return

    fechas = list(daily_prices.keys())
    existing_bcv = get_existing_bcv(fechas)

    rows = []
    for fecha, precio in daily_prices.items():
        row = {
            "date": fecha,
            "tasa_binance": precio,
            "updated_at": "now()"
        }
        # Si ya existe tasa_bcv, la incluimos para que el upsert NO la borre
        if fecha in existing_bcv:
            row["tasa_bcv"] = existing_bcv[fecha]
        # Si no existe, no incluimos tasa_bcv → Supabase la dejará como null solo si el registro es nuevo,
        # pero si el registro ya existía y no tenía tasa_bcv, tampoco la borramos.
        # En cualquier caso, al no incluirla o incluirla solo cuando existe, evitamos sobrescribir con null.
        rows.append(row)

    print(f"Preparando upsert de {len(rows)} filas...")
    result = supabase.table("exchange_rates").upsert(
        rows,
        on_conflict="date"
    ).execute()

    if hasattr(result, 'error') and result.error:
        print(f"Error: {result.error}")
    else:
        print("✅ Backfill de Binance completado sin borrar BCV.")

if __name__ == "__main__":
    daily_prices = fetch_p2p_history()
    save_rows(daily_prices)
