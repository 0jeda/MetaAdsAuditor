from meta_ads_collector import MetaAdsCollector
import json
from datetime import datetime

BUSQUEDAS = [
    # Por keyword general
    {"type": "query", "query": "venta de casas slp", "country": "MX"},
    {"type": "query", "query": "infonavit san luis potosi", "country": "MX"},
    {"type": "query", "query": "vende tu casa", "country": "MX"},

    # Por página específica
    {"type": "page_id", "page_id": "104602255634120",  "nombre": "Vivite Traspasame"},
    {"type": "page_id", "page_id": "102703976024734",  "nombre": "Garantia Inmobiliaria"},
    {"type": "page_id", "page_id": "980742165122594",  "nombre": "Ubicanton Chihuahua"},
    {"type": "page_name", "page_name": "tercerosinmuebles", "nombre": "Vivite Terceros Inmuebles"},
    {"type": "page_name", "page_name": "grupocimaslp",     "nombre": "Grupo Cima"},
    {"type": "page_name", "page_name": "ubicantonmx",      "nombre": "Ubicanton Nacional"},
]

resultados = []

with MetaAdsCollector() as collector:
    for busqueda in BUSQUEDAS:
        try:
            if busqueda["type"] == "query":
                origen = busqueda["query"]
                print(f"🔍 Buscando keyword: {origen}...")
                ads = collector.search(
                    query=busqueda["query"],
                    country=busqueda["country"],
                    max_results=20
                )

            elif busqueda["type"] == "page_id":
                origen = busqueda["nombre"]
                print(f"📄 Buscando página por ID: {origen}...")
                ads = collector.collect_by_page_id(
                    busqueda["page_id"],
                    country="MX"
                )

            elif busqueda["type"] == "page_name":
                origen = busqueda["nombre"]
                print(f"📄 Buscando página por nombre: {origen}...")
                ads = collector.collect_by_page_name(
                    busqueda["page_name"],
                    country="MX"
                )

            for ad in ads:
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
                    "busqueda_origen": origen
                })

        except Exception as e:
            print(f"⚠️ Error en {busqueda.get('nombre', busqueda.get('query', ''))}: {e}")
            continue

fecha = datetime.now().strftime("%Y-%m-%d")
archivo = f"competencia_{fecha}.json"
with open(archivo, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(resultados)} anuncios guardados en {archivo}")