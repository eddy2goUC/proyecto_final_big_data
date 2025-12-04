import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import os
import re
from typing import List, Dict
from Helpers import Funciones


class WebScraping:
    """Clase para realizar web scraping y extracción de enlaces"""
    
    def __init__(self, dominio_base: str = "https://infolibros.org/libros-pdf-gratis/negocios/economia/"):
        """
        Inicializa la clase WebScraping
        
        Args:
            dominio_base: Dominio base para validar enlaces
        """
        self.dominio_base = dominio_base
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_links(self, url: str, listado_extensiones: List[str] = None) -> List[Dict]:
        """
        Extrae links de libros según listado de extensiones (PDF)
        
        Args:
            url: URL de la página a analizar
            listado_extensiones: Lista de extensiones a filtrar (ej: ['pdf'])
            
        Returns:
            Lista de diccionarios con 'url', 'type' y 'title' de cada enlace encontrado
        """
        print(f"Extrayendo links de: {url}")

        if listado_extensiones is None:
            listado_extensiones = ['pdf']
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Buscar todos los contenedores de libros
            book_containers = soup.find_all('div', class_='caja-pdfs')
            
            if not book_containers:
                # Intentar otro selector común
                book_containers = soup.find_all('div', class_=re.compile(r'caja|libro|book'))
            
            print(f"Encontrados {len(book_containers)} contenedores de libros")
            
            for container in book_containers:
                try:
                    # Extraer título del libro
                    title_elem = container.find(['h2', 'h3', 'h4', 'strong', 'b'])
                    if title_elem:
                        # Limpiar el título (eliminar números como #1, #2, etc.)
                        title = re.sub(r'^#\d+\s*', '', title_elem.get_text(strip=True))
                    else:
                        # Si no encuentra título, usar el primer texto del contenedor
                        title = container.get_text(strip=True).split('\n')[0]
                        title = re.sub(r'^#\d+\s*', '', title)
                    
                    # Buscar enlace de descarga
                    download_link = container.find('a', string=re.compile(r'descargar', re.IGNORECASE))
                    
                    if not download_link:
                        # Buscar cualquier enlace que contenga .pdf
                        download_link = container.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
                    
                    if download_link and download_link.get('href'):
                        href = download_link['href']
                        full_url = urljoin(url, href)
                        
                        # Verificar si es un PDF (por extensión o por patrón en la URL)
                        for ext in listado_extensiones:
                            if full_url.lower().endswith(f'.{ext.lower()}'):
                                links.append({
                                    'url': full_url,
                                    'type': ext.lower(),
                                    'title': title[:200]  # Limitar longitud del título
                                })
                                break
                        else:
                            # Si no termina en .pdf pero parece un enlace de descarga
                            if 'pdf' in full_url.lower() or 'dropbox' in full_url.lower():
                                links.append({
                                    'url': full_url,
                                    'type': 'pdf',
                                    'title': title[:200]
                                })
                
                except Exception as e:
                    print(f"Error procesando contenedor: {e}")
                    continue
            
            # Si no encontramos contenedores, buscar enlaces PDF directamente
            if not links:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        for ext in listado_extensiones:
                            if full_url.lower().endswith(f'.{ext.lower()}'):
                                title = link.get_text(strip=True) or f"PDF_{len(links)+1}"
                                links.append({
                                    'url': full_url,
                                    'type': ext.lower(),
                                    'title': title[:200]
                                })
                                break
            
            print(f"Se encontraron {len(links)} enlaces PDF")
            return links
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []
        except Exception as e:
            print(f"Error procesando {url}: {e}")
            return []
    
    def extraer_todos_los_links(self, url_inicial: str, json_file_path: str, 
                                listado_extensiones: List[str] = None,
                                max_iteraciones: int = 100) -> Dict:
        """
        Extrae todos los links de libros desde una URL inicial
        
        Args:
            url_inicial: URL inicial para comenzar la extracción
            json_file_path: Ruta del archivo JSON para guardar/cargar links
            listado_extensiones: Lista de extensiones a filtrar
            max_iteraciones: Número máximo de iteraciones (no se usa mucho aquí, pero se mantiene)
            
        Returns:
            Diccionario con el resultado de la extracción
        """
        if listado_extensiones is None:
            listado_extensiones = ['pdf']
        
        # Cargar links existentes del archivo JSON
        all_links = self._cargar_links_desde_json(json_file_path)
        
        # Si no hay links, extraer de la URL inicial
        if not all_links:
            print(f"Extrayendo links de la URL inicial: {url_inicial}")
            all_links = self.extract_links(url_inicial, listado_extensiones)
        
        # Guardar en JSON
        json_output = {"links": all_links}
        self._guardar_links_en_json(json_file_path, json_output)
        
        print(f"Finalizado: Se encontraron {len(all_links)} links en total")
        
        return {
            'success': True,
            'total_links': len(all_links),
            'links': all_links,
            'iteraciones': 1  # Solo una iteración para esta página
        }
    
    def _cargar_links_desde_json(self, json_file_path: str) -> List[Dict]:
        """Carga links desde un archivo JSON"""
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                all_links = json_data.get("links", [])
                print(f"Cargados {len(all_links)} links desde {json_file_path}")
                return all_links
            except json.JSONDecodeError:
                print(f"Advertencia: {json_file_path} contiene JSON inválido. Inicializando con lista vacía.")
                return []
        else:
            print(f"{json_file_path} no encontrado. Se creará un nuevo archivo.")
            return []
    
    def _guardar_links_en_json(self, json_file_path: str, data: Dict):
        """Guarda links en un archivo JSON"""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True) if os.path.dirname(json_file_path) else None
            
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Links guardados en {json_file_path}")
        except Exception as e:
            print(f"Error al guardar JSON: {e}")
    
    def descargar_pdfs(self, json_file_path: str, carpeta_destino: str = "static/uploads") -> Dict:
        """
        Recorre el archivo JSON y descarga los archivos PDF en la carpeta especificada
        
        Args:
            json_file_path: Ruta del archivo JSON con los links
            carpeta_destino: Carpeta donde se descargarán los PDFs (default: static/uploads)
            
        Returns:
            Diccionario con el resultado de la descarga
        """
        try:
            # Cargar links desde JSON
            all_links = self._cargar_links_desde_json(json_file_path)
            
            # Filtrar solo links PDF
            pdf_links = [link for link in all_links if link.get('type') == 'pdf']
            
            if not pdf_links:
                return {
                    'success': True,
                    'mensaje': 'No hay archivos PDF para descargar',
                    'descargados': 0,
                    'errores': 0
                }
            
            # Crear carpeta de destino si no existe
            Funciones.crear_carpeta(carpeta_destino)
            
            # Borrar contenido de la carpeta antes de descargar
            print(f"Limpiando contenido de la carpeta: {carpeta_destino}")
            Funciones.borrar_contenido_carpeta(carpeta_destino)
            
            # Descargar PDFs
            descargados = 0
            errores = 0
            archivos_errores = []
            
            print(f"Iniciando descarga de {len(pdf_links)} archivos PDF...")
            
            for i, link in enumerate(pdf_links, 1):
                pdf_url = link['url']
                title = link.get('title', f'libro_{i}')
                
                try:
                    # Crear nombre de archivo seguro a partir del título
                    safe_title = re.sub(r'[^\w\s-]', '', title)
                    safe_title = re.sub(r'[-\s]+', '_', safe_title)
                    nombre_archivo = f"{i:03d}_{safe_title[:50]}.pdf"
                    
                    # Si el nombre está vacío, generar uno
                    if not nombre_archivo or nombre_archivo == '.pdf':
                        nombre_archivo = f"archivo_{i}.pdf"
                    
                    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
                    
                    # Descargar archivo
                    print(f"Descargando [{i}/{len(pdf_links)}]: {title[:50]}...")
                    
                    # Para enlaces de Dropbox, asegurar que sea enlace de descarga directa
                    if 'dropbox.com' in pdf_url or 'dropboxusercontent.com' in pdf_url:
                        if 'dl=0' in pdf_url:
                            pdf_url = pdf_url.replace('dl=0', 'dl=1')
                        elif '?' not in pdf_url:
                            pdf_url = pdf_url + '?dl=1'
                        elif '?' in pdf_url and 'dl=' not in pdf_url:
                            pdf_url = pdf_url + '&dl=1'
                    
                    # Headers para simular navegador
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/pdf, */*',
                        'Referer': 'https://infolibros.org/'
                    }
                    
                    response = self.session.get(pdf_url, headers=headers, stream=True, timeout=60)
                    response.raise_for_status()
                    
                    # Guardar archivo
                    with open(ruta_archivo, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verificar que el archivo no esté vacío
                    if os.path.getsize(ruta_archivo) > 0:
                        file_size = os.path.getsize(ruta_archivo) / (1024 * 1024)  # MB
                        print(f"  ✓ Descargado ({file_size:.2f} MB)")
                        descargados += 1
                    else:
                        print(f"  ✗ Archivo vacío")
                        errores += 1
                        archivos_errores.append({
                            'url': pdf_url,
                            'error': 'Archivo descargado vacío'
                        })
                        # Eliminar archivo vacío
                        os.remove(ruta_archivo)
                    
                except Exception as e:
                    errores += 1
                    archivos_errores.append({
                        'url': pdf_url,
                        'error': str(e)
                    })
                    print(f"Error al descargar {pdf_url}: {e}")
            
            resultado = {
                'success': True,
                'total': len(pdf_links),
                'descargados': descargados,
                'errores': errores,
                'carpeta_destino': carpeta_destino
            }
            
            if archivos_errores:
                resultado['archivos_con_error'] = archivos_errores
            
            print(f"\nDescarga completada:")
            print(f"  Total: {len(pdf_links)}")
            print(f"  Descargados: {descargados}")
            print(f"  Errores: {errores}")
            
            return resultado
            
        except Exception as e:
            print(f"Error en descargar_pdfs: {e}")
            return {
                'success': False,
                'error': str(e),
                'descargados': 0,
                'errores': 0
            }
    
    def close(self):
        """Cierra la sesión de requests"""
        self.session.close()