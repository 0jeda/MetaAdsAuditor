from meta_ads_collector import MetaAdsCollector
import json
from datetime import datetime

BUSQUEDAS = [
    {"query": "venta de casas slp", "country": "MX"},
    {"query": "infonavit san luis potosi", "country": "MX"},
    {"query": "vende tu casa", "country": "MX"},
]

resultados = []

with MetaAdsCollector() as collector:
    for busqueda in BUSQUEDAS:
        print(f"Buscando: {busqueda['query']}...")
        for ad in collector.search(
            query=busqueda["query"],
            country=busqueda["country"],
            max_results=20
        ):
            # Extraer texto del creativo
            texto = ""
            imagen_url = ""
            video_url = ""
            
            if ad.creatives:
                c = ad.creatives[0]
                texto = c.body or ""
                imagen_url = c.image_url or ""
                video_url = c.video_url or c.video_hd_url or ""

            resultados.append({
                "pagina": ad.page.name,
                "pagina_url": ad.page.page_url,
                "pagina_likes": ad.page.likes,
                "id": ad.id,
                "activo": ad.is_active,
                "fecha_inicio": str(ad.delivery_start_time),
                "fecha_fin": str(ad.delivery_stop_time),
                "texto": texto,
                "imagen_url": imagen_url,
                "video_url": video_url,
                "cta": ad.creatives[0].cta_text if ad.creatives else "",
                "plataformas": ad.publisher_platforms,
                "busqueda_origen": busqueda["query"]
            })

fecha = datetime.now().strftime("%Y-%m-%d")
archivo = f"competencia_{fecha}.json"
with open(archivo, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"✅ {len(resultados)} anuncios guardados en {archivo}")
