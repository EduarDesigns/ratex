import os
import requests
from datetime import date
from supabase import create_client, Client

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_bcv_history(start: str, end: str):
    """
    Obtiene todo el historial del BCV desde la API de rafnixg.
    start y end en formato YYYY-MM-DD.
    Retorna una lista de dicts listos para Supabase.
    """
    api_url = f"https://bcv-api.rafnixg.dev/rates/history?start_date={start}&end_date={end}"
    
    print(f"Consultando {api_url} ...")
    try:
        resp = requests.get(api_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error al consultar la API: {e}")
        return []

    rates = data.get("rates", [])
    print(f"Se recibieron {len(rates)} registros.")

    rows = []
    for r in rates:
        rows.append({
            "date": r["date"],
            "tasa_bcv": r["dollar"],
            "tasa_binance": None,        # ← se deja null por ahora
            "updated_at": "now()"
        })

    return rows

def save_rows(rows):
    """Inserta o actualiza en bloque usando upsert."""
    if not rows:
        print("No hay filas para guardar.")
        return

    print(f"Insertando/actualizando {len(rows)} filas en Supabase...")
    result = supabase.table("exchange_rates").upsert(
        rows,
        on_conflict="date"
    ).execute()

    # Verificamos que no haya errores
    if hasattr(result, 'error') and result.error:
        print(f"Error de Supabase: {result.error}")
    else:
        print("¡Backfill completado exitosamente!")

if __name__ == "__main__":
    # Rango: 1 de enero hasta hoy (o hasta donde prefieras)
    rows = fetch_bcv_history("2026-01-01", "2026-05-03")
    save_rows(rows)
