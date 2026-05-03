import os
import json
from supabase import create_client, Client

# Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Datos crudos obtenidos de la API (los proporcionaste)
RAW_DATA = {
    "start_date": "2026-01-01",
    "end_date": "2026-05-03",
    "rates": [
        {"dollar": 489.5547, "date": "2026-05-03"},
        {"dollar": 489.5547, "date": "2026-05-02"},
        {"dollar": 489.5547, "date": "2026-05-01"},
        {"dollar": 489.5547, "date": "2026-04-30"},
        {"dollar": 487.1192, "date": "2026-04-29"},
        {"dollar": 486.1955, "date": "2026-04-28"},
        {"dollar": 485.2251, "date": "2026-04-27"},
        {"dollar": 484.7404, "date": "2026-04-26"},
        {"dollar": 484.7404, "date": "2026-04-25"},
        {"dollar": 483.8695, "date": "2026-04-24"},
        {"dollar": 483.8695, "date": "2026-04-23"},
        {"dollar": 482.7586, "date": "2026-04-22"},
        {"dollar": 482.7586, "date": "2026-04-21"},
        {"dollar": 481.6989, "date": "2026-04-20"},
        {"dollar": 481.2177, "date": "2026-04-19"},
        {"dollar": 481.2177, "date": "2026-04-18"},
        {"dollar": 481.2177, "date": "2026-04-17"},
        {"dollar": 480.2572, "date": "2026-04-16"},
        {"dollar": 479.7775, "date": "2026-04-15"},
        {"dollar": 478.5811, "date": "2026-04-14"},
        {"dollar": 477.6259, "date": "2026-04-13"},
        {"dollar": 477.1488, "date": "2026-04-12"},
        {"dollar": 477.1488, "date": "2026-04-11"},
        {"dollar": 477.1488, "date": "2026-04-10"},
        {"dollar": 475.9583, "date": "2026-04-09"},
        {"dollar": 475.0083, "date": "2026-04-08"},
        {"dollar": 474.5338, "date": "2026-04-07"},
        {"dollar": 474.5338, "date": "2026-04-06"},
        {"dollar": 474.0598, "date": "2026-04-05"},
        {"dollar": 474.0598, "date": "2026-04-04"},
        {"dollar": 474.0598, "date": "2026-04-03"},
        {"dollar": 474.0598, "date": "2026-04-02"},
        {"dollar": 473.9176, "date": "2026-04-01"},
        {"dollar": 473.8702, "date": "2026-03-31"},
        {"dollar": 473.8702, "date": "2026-03-30"},
        {"dollar": 471.7004, "date": "2026-03-29"},
        {"dollar": 471.7004, "date": "2026-03-28"},
        {"dollar": 471.7004, "date": "2026-03-27"},
        {"dollar": 468.5145, "date": "2026-03-26"},
        {"dollar": 466.6014, "date": "2026-03-25"},
        {"dollar": 462.6687, "date": "2026-03-24"},
        {"dollar": 459.4525, "date": "2026-03-23"},
        {"dollar": 457.0757, "date": "2026-03-22"},
        {"dollar": 457.0757, "date": "2026-03-21"},
        {"dollar": 457.0757, "date": "2026-03-20"},
        {"dollar": 455.2547, "date": "2026-03-19"},
        {"dollar": 455.2547, "date": "2026-03-18"},
        {"dollar": 451.5072, "date": "2026-03-17"},
        {"dollar": 448.3686, "date": "2026-03-16"},
        {"dollar": 446.8048, "date": "2026-03-15"},
        {"dollar": 446.8048, "date": "2026-03-14"},
        {"dollar": 446.8048, "date": "2026-03-13"},
        {"dollar": 443.2587, "date": "2026-03-12"},
        {"dollar": 440.9657, "date": "2026-03-11"},
        {"dollar": 438.205, "date": "2026-03-10"},
        {"dollar": 436.2419, "date": "2026-03-09"},
        {"dollar": 433.1664, "date": "2026-03-07"},
        {"dollar": 433.1664, "date": "2026-03-06"},
        {"dollar": 427.9302, "date": "2026-03-05"},
        {"dollar": 427.9302, "date": "2026-03-04"},
        {"dollar": 405.3518, "date": "2026-02-20"},
        {"dollar": 402.3343, "date": "2026-02-19"},
        {"dollar": 398.7456, "date": "2026-02-18"},
        {"dollar": 396.3674, "date": "2026-02-17"},
        {"dollar": 396.3674, "date": "2026-02-16"},
        {"dollar": 396.3674, "date": "2026-02-15"},
        {"dollar": 396.3674, "date": "2026-02-14"},
        {"dollar": 396.3674, "date": "2026-02-13"},
        {"dollar": 393.2216, "date": "2026-02-12"},
        {"dollar": 390.2944, "date": "2026-02-11"},
        {"dollar": 388.7394, "date": "2026-02-10"},
        {"dollar": 385.272, "date": "2026-02-09"},
        {"dollar": 382.6318, "date": "2026-02-08"},
        {"dollar": 382.6318, "date": "2026-02-07"},
        {"dollar": 382.6318, "date": "2026-02-06"},
        {"dollar": 381.1074, "date": "2026-02-05"},
        {"dollar": 378.4582, "date": "2026-02-04"},
        {"dollar": 375.0825, "date": "2026-02-03"},
        {"dollar": 372.1057, "date": "2026-02-02"},
        {"dollar": 370.2544, "date": "2026-02-01"},
        {"dollar": 370.2544, "date": "2026-01-31"},
        {"dollar": 370.2544, "date": "2026-01-30"},
        {"dollar": 367.3069, "date": "2026-01-29"},
        {"dollar": 363.6623, "date": "2026-01-28"},
        {"dollar": 361.4906, "date": "2026-01-27"},
        {"dollar": 358.9247, "date": "2026-01-26"},
        {"dollar": 355.5528, "date": "2026-01-25"},
        {"dollar": 355.5528, "date": "2026-01-24"},
        {"dollar": 355.5528, "date": "2026-01-23"},
        {"dollar": 352.7063, "date": "2026-01-22"},
        {"dollar": 349.9272, "date": "2026-01-21"},
        {"dollar": 347.2631, "date": "2026-01-20"},
        {"dollar": 344.5071, "date": "2026-01-19"},
        {"dollar": 344.5071, "date": "2026-01-18"},
        {"dollar": 344.5071, "date": "2026-01-17"},
        {"dollar": 344.5071, "date": "2026-01-16"},
        {"dollar": 341.7425, "date": "2026-01-15"},
        {"dollar": 339.1495, "date": "2026-01-14"},
        {"dollar": 336.4596, "date": "2026-01-13"},
        {"dollar": 330.3751, "date": "2026-01-12"},
        {"dollar": 330.3751, "date": "2026-01-11"},
        {"dollar": 330.3751, "date": "2026-01-10"},
        {"dollar": 330.3751, "date": "2026-01-09"},
        {"dollar": 325.3894, "date": "2026-01-08"},
        {"dollar": 321.0323, "date": "2026-01-07"},
        {"dollar": 311.8814, "date": "2026-01-06"},
        {"dollar": 308.1546, "date": "2026-01-05"},
        {"dollar": 304.6796, "date": "2026-01-04"},
        {"dollar": 304.6796, "date": "2026-01-03"},
        {"dollar": 304.6796, "date": "2026-01-02"},
        {"dollar": 301.3709, "date": "2026-01-01"}
    ]
}

def save_historical_rates():
    rows = []
    for r in RAW_DATA["rates"]:
        rows.append({
            "date": r["date"],
            "tasa_bcv": r["dollar"],
            "tasa_binance": None,
            "updated_at": "now()"
        })

    print(f"Se prepararon {len(rows)} registros para insertar/actualizar...")

    # Upsert en lote
    result = supabase.table("exchange_rates").upsert(
        rows,
        on_conflict="date"
    ).execute()

    if hasattr(result, 'error') and result.error:
        print(f"Error al guardar: {result.error}")
    else:
        print("✅ Backfill completado exitosamente.")

if __name__ == "__main__":
    save_historical_rates()
