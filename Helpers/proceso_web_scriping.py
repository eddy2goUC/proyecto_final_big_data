import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

def extraer_noticias_eltiempo(total_noticias=100):
    url_base = "https://www.eltiempo.com"
    noticias = []
    
    # Secciones para extraer noticias
    secciones = [
        "/ultimas-noticias",
        "/politica",
        "/economia",
        "/deportes",
        "/tecnologia",
        "/cultura",
        "/medio-ambiente",
        "/salud",
        "/educacion"
    ]
    
    for seccion in secciones:
        if len(noticias) >= total_noticias:
            break
            
        # Extraer múltiples páginas de cada sección
        for pagina in range(1, 6):
            if len(noticias) >= total_noticias:
                break
                
            try:
                if pagina == 1:
                    url = f"{url_base}{seccion}"
                else:
                    url = f"{url_base}{seccion}?page={pagina}"
                
                respuesta = requests.get(url, timeout=10)
                soup = BeautifulSoup(respuesta.content, 'html.parser')
                
                # Buscar elementos de noticias
                elementos_noticias = []
                
                # Diferentes selectores para encontrar artículos
                selectores = [
                    'article',
                    '.article',
                    '.news',
                    '.noticia',
                    '.card',
                    '.headline',
                    '[data-type="article"]'
                ]
                
                for selector in selectores:
                    elementos = soup.select(selector)
                    if elementos:
                        elementos_noticias.extend(elementos)
                
                # Procesar cada elemento de noticia
                for elemento in elementos_noticias[:30]:
                    if len(noticias) >= total_noticias:
                        break
                    
                    try:
                        # Extraer título
                        titulo_elemento = elemento.find(['h2', 'h3', 'h1', 'a'])
                        titulo = titulo_elemento.get_text(strip=True) if titulo_elemento else ""
                        
                        # Extraer enlace
                        enlace_elemento = elemento.find('a', href=True)
                        if enlace_elemento:
                            href = enlace_elemento['href']
                            if href.startswith('/'):
                                href = url_base + href
                            elif not href.startswith('http'):
                                href = url_base + '/' + href.lstrip('/')
                            
                            # Filtrar solo enlaces de El Tiempo
                            if 'eltiempo.com' in href and not any(x in href for x in ['foto', 'video', 'galeria']):
                                # Extraer categoría de la URL
                                categoria = seccion.replace('/', '').replace('-', ' ').title()
                                if categoria == "Ultimas Noticias":
                                    categoria = "General"
                                
                                noticias.append({
                                    'periodico': 'El Tiempo',
                                    'titulo': titulo[:500],
                                    'enlace': href,
                                    'categoria': categoria,
                                    'fecha_extraccion': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                    except:
                        continue
                
                time.sleep(1)
                
            except:
                continue
    
    # Crear DataFrame y limpiar duplicados
    df = pd.DataFrame(noticias)
    df = df.drop_duplicates(subset=['titulo', 'enlace'])
    
    # Asegurar exactamente 100 registros
    if len(df) > total_noticias:
        df = df.head(total_noticias)
    
    # Guardar en CSV
    df.to_csv('noticias_eltiempo_100.csv', index=False, encoding='utf-8-sig')
    
    return len(df)

# Ejecutar
cantidad = extraer_noticias_eltiempo(100)
print(f"Se extrajeron {cantidad} noticias de El Tiempo")