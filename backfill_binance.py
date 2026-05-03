import os
import requests
from datetime import datetime, date
from collections import OrderedDict
from supabase import create_client, Client

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_p2p_history():
    """
    Obtiene el historial de precios P2P desde la API de p2pvenezuela.com
    y extrae el primer precio de cada día (el más temprano).
    """
    api_url = "https://www.p2pvenezuela.com/api/p2p/historial/90?pair=VES&t=1777844455169"
    
    print(f"Consultando {api_url} ...")
    try:
        resp = requests.get(api_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error al consultar la API: {e}")
        return []

    print(f"Se recibieron {len(data)} registros en total.")
    
    # Agrupar por fecha y tomar el primer precio de cada día
    # Usamos un diccionario ordenado para preservar el orden cronológico
    daily_first_price = OrderedDict()
    
    for entry in data:
        precio_str = entry.get("precio")
        created_at_str = entry.get("created_at")
        
        if not precio_str or not created_at_str:
            continue
        
        try:
            # Parsear la fecha ISO 8601
            dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            fecha_str = dt.strftime("%Y-%m-%d")
            precio = float(precio_str)
        except (ValueError, TypeError) as e:
            print(f"Error parseando entrada {entry}: {e}")
            continue
        
        # Si aún no tenemos un precio para esta fecha, lo guardamos
        if fecha_str not in daily_first_price:
            daily_first_price[fecha_str] = precio
    
    print(f"Se extrajeron precios para {len(daily_first_price)} días distintos.")
    
    # Convertir a lista de filas para Supabase
    rows = []
    for fecha, precio in daily_first_price.items():
        rows.append({
            "date": fecha,
            "tasa_binance": precio,
            "tasa_bcv": None,           # No tocamos la tasa BCV
            "updated_at": "now()"
        })
    
    return rows

def save_rows(rows):
    """Inserta o actualiza en Supabase usando upsert."""
    if not rows:
        print("No hay filas para guardar.")
        return
    
    print(f"Insertando/actualizando {len(rows)} filas en Supabase...")
    result = supabase.table("exchange_rates").upsert(
        rows,
        on_conflict="date"
    ).execute()
    
    if hasattr(result, 'error') and result.error:
        print(f"Error de Supabase: {result.error}")
    else:
        print("✅ Backfill de Binance completado exitosamente.")

if __name__ == "__main__":
    rows = fetch_p2p_history()
    save_rows(rows)
