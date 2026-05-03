import os
import re
import requests
from datetime import date
from lxml import html  # Usaremos lxml para aprovechar XPath
from supabase import create_client, Client
import urllib3
# Suprimir la advertencia de SSL mientras hacemos scraping al BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


        
# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")  # service_role
supabase: Client = create_client(url, key)

# --- NUEVA Función para la tasa BCV (Usando lxml y el XPath exacto) ---
def get_bcv_rate():
    """
    Extrae la tasa de cambio oficial del BCV (USD a VES) usando lxml y XPath.
    Se desactiva la verificación SSL porque el entorno a veces no confía en el certificado del BCV.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    
    try:
        # --- CAMBIO CLAVE ---
        # Añadimos verify=False para ignorar la validación del certificado SSL del BCV
        response = requests.get("https://www.bcv.org.ve/", headers=headers, timeout=20, verify=False)
        response.raise_for_status()

        tree = html.fromstring(response.content)
        
        elemento_tasa = tree.xpath('/html/body/div[4]/div/div[2]/div/div[1]/div[1]/section[1]/div/div[2]/div/div[7]/div/div/div[2]/strong')
        
        if elemento_tasa:
            texto_bruto = elemento_tasa[0].text_content().strip()
            print(f"BCV - Texto encontrado con XPath: '{texto_bruto}'")
            
            busca_numero = re.search(r'(\d+,\d+)', texto_bruto)
            if busca_numero:
                tasa_str = busca_numero.group(1).replace(',', '.')
                tasa_float = float(tasa_str)
                print(f"BCV - Tasa extraída con éxito: {tasa_float}")
                return tasa_float
            else:
                print(f"BCV - ERROR: No se encontró un número válido en el texto '{texto_bruto}'")
                return None
        else:
            print("BCV - ERROR: El XPath no encontró ningún elemento.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"BCV - ERROR de conexión: {e}")
        return None
    except Exception as e:
        print(f"BCV - ERROR inesperado: {e}")
        return None

# --- Función para la tasa Binance P2P (Se mantiene igual) ---
def get_binance_p2p_rate():
    """Promedio de los 3 mejores anuncios P2P USDT/VES con PagoMóvil."""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "page": 1,
        "rows": 20,
        "asset": "USDT",
        "fiat": "VES",
        "tradeType": "BUY",
        "payTypes": ["PagoMovil"]
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        ads = data.get("data", [])

        if not ads:
            print("Binance - No se encontraron anuncios PagoMóvil")
            return None

        ads_sorted = sorted(ads, key=lambda x: float(x["adv"]["price"]))
        top3 = ads_sorted[:3]
        prices = [float(ad["adv"]["price"]) for ad in top3]
        average = sum(prices) / len(prices)
        print(f"Binance - Tasa P2P promedio (top 3): {average}")
        return average

    except Exception as e:
        print(f"Binance - ERROR: {e}")
        return None

# --- Función para guardar en Supabase (Se mantiene igual) ---
def save_daily_rate():
    today = date.today()
    print(f"--- Iniciando actualización para {today} ---")
    tasa_bcv = get_bcv_rate()
    tasa_binance = get_binance_p2p_rate()

    if tasa_bcv is None and tasa_binance is None:
        print("No se pudo obtener ninguna tasa. Abortando.")
        return

    data = {
        "date": str(today),
        "tasa_bcv": tasa_bcv,
        "tasa_binance": tasa_binance,
        "updated_at": "now()"
    }

    result = supabase.table("exchange_rates").upsert(data, on_conflict="date").execute()
    print("Registro guardado exitosamente en Supabase.")
    print(result)

if __name__ == "__main__":
    save_daily_rate()
