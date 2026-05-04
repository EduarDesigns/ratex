import os
import re
import requests
import urllib3
from datetime import date
from lxml import html
from supabase import create_client, Client

# Suprimir advertencia SSL para el BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ------------------------------------------------------------
# 1. Tasa BCV
# ------------------------------------------------------------
def get_bcv_rate():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    try:
        resp = requests.get("https://www.bcv.org.ve/", headers=headers, timeout=20, verify=False)
        resp.raise_for_status()
        tree = html.fromstring(resp.content)
        elem = tree.xpath('/html/body/div[4]/div/div[2]/div/div[1]/div[1]/section[1]/div/div[2]/div/div[7]/div/div/div[2]/strong')
        if elem:
            texto = elem[0].text_content().strip()
            match = re.search(r'(\d+,\d+)', texto)
            if match:
                return float(match.group(1).replace(',', '.'))
    except Exception as e:
        print(f"BCV error: {e}")
    return None

# ------------------------------------------------------------
# 2. Binance P2P USDT/VES (PagoMóvil)
# ------------------------------------------------------------
def get_binance_p2p_ves_rate():
    return get_p2p_price("VES", ["PagoMovil"])

# ------------------------------------------------------------
# 3. Binance P2P USDT/COP (Nequi) – NUEVO
# ------------------------------------------------------------
def get_binance_p2p_cop_rate():
    return get_p2p_price("COP", ["Nequi"])

def get_p2p_price(fiat, pay_types):
    """Obtiene promedio de los 3 mejores anuncios (precio más bajo) para comprar USDT."""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "page": 1,
        "rows": 20,
        "asset": "USDT",
        "fiat": fiat,
        "tradeType": "BUY",
        "payTypes": pay_types
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            print(f"P2P {fiat}: sin anuncios con {pay_types}")
            return None
        # Ordenar por precio ascendente
        sorted_ads = sorted(data, key=lambda x: float(x["adv"]["price"]))
        top3 = sorted_ads[:3]
        avg = sum(float(ad["adv"]["price"]) for ad in top3) / len(top3)
        print(f"P2P {fiat} ({pay_types}): top 3 avg = {avg}")
        return avg
    except Exception as e:
        print(f"P2P {fiat} error: {e}")
        return None

# ------------------------------------------------------------
# Guardar en Supabase
# ------------------------------------------------------------
def save_daily_rate():
    today = date.today()
    print(f"--- Iniciando actualización para {today} ---")

    tasa_bcv = get_bcv_rate()
    tasa_ves = get_binance_p2p_ves_rate()
    tasa_cop = get_binance_p2p_cop_rate()

    if tasa_bcv is None and tasa_ves is None and tasa_cop is None:
        print("No se pudo obtener ninguna tasa. Saliendo con error.")
        exit(1)

    data = {
        "date": str(today),
        "tasa_bcv": tasa_bcv,
        "tasa_binance": tasa_ves,
        "tasa_binance_cop": tasa_cop,
        "updated_at": "now()"
    }

    result = supabase.table("exchange_rates").upsert(data, on_conflict="date").execute()
    print("Registro guardado:", result)

if __name__ == "__main__":
    save_daily_rate()
