from meta_ads_collector import MetaAdsCollector
import json
import requests
import os
from datetime import datetime

BUSQUEDAS = [
    {"type": "query", "query": "venta de casas slp", "country": "MX"},
    {"type": "query", "query": "infonavit san luis potosi", "country": "MX"},
    {"type": "query", "query": "vende tu casa", "country": "MX"},
    {"type": "page_id", "page_id": "104602255634120",  "nombre": "Vivite Traspasame"},
    {"type": "page_id", "page_id": "102703976024734",  "nombre": "Garantia Inmobiliaria"},
    {"type": "page_id", "page_id": "980742165122594",  "nombre": "Ubicanton Chihuahua"},
    {"type": "page_name", "page_name": "tercerosinmuebles", "nombre": "Vivite Terceros Inmuebles"},
    {"type": "page_name", "page_name": "grupocimaslp",     "nombre": "Grupo Cima"},
    {"type": "page_name", "page_name": "ubicantonmx",      "nombre": "Ubicanton Nacional"},
]

# Palabras clave para filtrar anuncios relevantes
KEYWORDS_RELEVANTES = ["infonavit", "casa", "slp", "inmobili", "vende", "garantia",
                       "traspaso", "adeudo", "credito", "vivienda", "potosi", "flipper"]

def nombre_carpeta_limpio(nombre):
    """Convierte el nombre de página en nombre válido para carpeta"""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in nombre).strip()[:40]

def descargar_archivo(url, ruta, headers=None):
    """Descarga un archivo y lo guarda en la ruta indicada"""
    if not url:
        return False
    try:
        h = headers or {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        r = requests.get(url, timeout=20, headers=h, stream=True)
        if r.status_code == 200:
            with open(ruta, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"    ⚠️ Error descargando: {e}")
    return False

def es_relevante(ad):
    """Filtra anuncios off-topic (pañales, gym, etc)"""
    texto = (ad.get("texto", "") + ad.get("pagina", "")).lower()
    return any(k in texto for k in KEYWORDS_RELEVANTES)

# Crear carpeta semanal principal
fecha = datetime.now().strftime("%Y-%m-%d")
carpeta_base = f"semana_{fecha}"
os.makedirs(carpeta_base, exist_ok=True)
print(f"\n📁 Carpeta de sesión: {carpeta_base}/\n")

resultados = []

with MetaAdsCollector() as collector:
    for busqueda in BUSQUEDAS:
        try:
            if busqueda["type"] == "query":
                origen = busqueda["query"]
                print(f"🔍 Keyword: {origen}")
                ads = collector.search(query=busqueda["query"], country=busqueda["country"], max_results=20)
            elif busqueda["type"] == "page_id":
                origen = busqueda["nombre"]
                print(f"📄 Página ID: {origen}")
                ads = collector.collect_by_page_id(busqueda["page_id"], country="MX")
            elif busqueda["type"] == "page_name":
                origen = busqueda["nombre"]
                print(f"📄 Página nombre: {origen}")
                ads = collector.collect_by_page_name(busqueda["page_name"], country="MX")

            for ad in ads:
                texto = ""
                imagen_url = ""
                video_url = ""

                if ad.creatives:
                    c = ad.creatives[0]
                    texto = c.body or ""
                    imagen_url = c.image_url or ""
                    video_url = c.video_url or c.video_hd_url or ""

                ad_data = {
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
                    "busqueda_origen": origen,
                    "imagen_local": "",
                    "video_local": "",
                }
                resultados.append(ad_data)

        except Exception as e:
            print(f"⚠️ Error en {busqueda.get('nombre', busqueda.get('query', ''))}: {e}")
            continue

print(f"\n✅ {len(resultados)} anuncios recopilados. Filtrando y descargando creativos...\n")

# Descargar creativos organizados por página
paginas_vistas = {}

for ad in resultados:
    if not es_relevante(ad):
        continue

    pagina = ad["pagina"]
    if pagina not in paginas_vistas:
        paginas_vistas[pagina] = 0

    # Crear estructura de carpetas: semana_FECHA/NombrePagina/imagenes + videos
    carpeta_pagina = os.path.join(carpeta_base, nombre_carpeta_limpio(pagina))
    carpeta_imagenes = os.path.join(carpeta_pagina, "imagenes")
    carpeta_videos = os.path.join(carpeta_pagina, "videos")
    os.makedirs(carpeta_imagenes, exist_ok=True)
    os.makedirs(carpeta_videos, exist_ok=True)

    ad_id = ad["id"][:10]
    dias = 0
    try:
        fecha_inicio = datetime.fromisoformat(ad["fecha_inicio"].replace(" ", "T").split(".")[0])
        dias = (datetime.now() - fecha_inicio).days
    except:
        pass

    # Descargar imagen
    if ad["imagen_url"]:
        nombre_img = f"{dias:03d}dias_{ad_id}.jpg"
        ruta_img = os.path.join(carpeta_imagenes, nombre_img)
        if not os.path.exists(ruta_img):
            ok = descargar_archivo(ad["imagen_url"], ruta_img)
            if ok:
                ad["imagen_local"] = ruta_img
                print(f"  🖼️  {pagina[:25]} → {nombre_img}")
        else:
            ad["imagen_local"] = ruta_img

    # Descargar video
    if ad["video_url"]:
        nombre_vid = f"{dias:03d}dias_{ad_id}.mp4"
        ruta_vid = os.path.join(carpeta_videos, nombre_vid)
        if not os.path.exists(ruta_vid):
            ok = descargar_archivo(ad["video_url"], ruta_vid)
            if ok:
                ad["video_local"] = ruta_vid
                print(f"  🎬  {pagina[:25]} → {nombre_vid}")
        else:
            ad["video_local"] = ruta_vid

    paginas_vistas[pagina] += 1

# Guardar JSON completo en la carpeta semanal
archivo_json = os.path.join(carpeta_base, f"competencia_{fecha}.json")
with open(archivo_json, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

# Resumen final
print(f"\n{'='*50}")
print(f"📊 RESUMEN DE SESIÓN — {fecha}")
print(f"{'='*50}")
print(f"📁 Carpeta: {carpeta_base}/")
print(f"📋 JSON: competencia_{fecha}.json")
print(f"🏢 Páginas con creativos descargados:")
for pagina, count in sorted(paginas_vistas.items(), key=lambda x: -x[1]):
    print(f"   • {pagina[:40]}: {count} anuncio(s)")
print(f"\n✅ Total anuncios guardados: {len(resultados)}")
print(f"{'='*50}\n")