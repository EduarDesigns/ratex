import os
import re
import requests
from datetime import date
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")  # service_role
supabase: Client = create_client(url, key)


def get_bcv_rate():
    """Extrae la tasa de cambio oficial del BCV (USD -> VES)."""
    try:
        response = requests.get("https://www.bcv.org.ve/", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        dolar_tag = soup.find(id="dolar")
        if not dolar_tag:
            dolar_tag = soup.find("div", class_="col-sm-6 col-xs-6 centrado")
            if dolar_tag:
                strong = dolar_tag.find("strong")
                if strong:
                    dolar_tag = strong

        if dolar_tag:
            text = dolar_tag.get_text(strip=True)
            match = re.search(r"[\d,\.]+", text.replace(",", ".").replace(" ", ""))
            if match:
                return float(match.group().replace(".", "").replace(",", "."))
    except Exception as e:
        print(f"Error BCV: {e}")
    return None


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
            print("No se encontraron anuncios PagoMóvil")
            return None

        # Ordenar por precio ascendente (mejor para comprar USDT)
        ads_sorted = sorted(ads, key=lambda x: float(x["adv"]["price"]))
        top3 = ads_sorted[:3]
        prices = [float(ad["adv"]["price"]) for ad in top3]
        return sum(prices) / len(prices)

    except Exception as e:
        print(f"Error Binance P2P: {e}")
        return None


def save_daily_rate():
    today = date.today()
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
    print("Registro guardado:", result)


if __name__ == "__main__":
    save_daily_rate()