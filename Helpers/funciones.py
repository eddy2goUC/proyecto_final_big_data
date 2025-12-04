import os
import zipfile
import requests
import json
import PyPDF2
from PIL import Image
import pytesseract
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename
from datetime import datetime

class Funciones:
    @staticmethod
    def crear_carpeta(ruta: str) -> bool:
        """Crea una carpeta si no existe"""
        try:
            if not os.path.exists(ruta):
                os.makedirs(ruta)
                print(f"Carpeta creada: {ruta}")
            return True
        except Exception as e:
            print(f"Error al crear carpeta: {e}")
            return False
    
    @staticmethod
    def listar_archivos_json(ruta_carpeta: str) -> List[Dict]:
        """
        Lista todos los archivos JSON en una carpeta
        
        Args:
            ruta_carpeta: Ruta de la carpeta a explorar
            
        Returns:
            Lista de diccionarios con información de cada archivo JSON
        """
        archivos_json = []
        try:
            print(f"Buscando archivos JSON en: {ruta_carpeta}")
            
            if not os.path.exists(ruta_carpeta):
                print(f"La carpeta no existe: {ruta_carpeta}")
                return []
            
            # Buscar archivos JSON en la carpeta (no recursivo)
            for archivo in os.listdir(ruta_carpeta):
                ruta_completa = os.path.join(ruta_carpeta, archivo)
                
                if os.path.isfile(ruta_completa) and archivo.lower().endswith('.json'):
                    try:
                        # Obtener información básica del archivo
                        stat_info = os.stat(ruta_completa)
                        fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)
                        
                        archivos_json.append({
                            'nombre': archivo,
                            'ruta': ruta_completa,
                            'tamaño_bytes': stat_info.st_size,
                            'tamaño_mb': stat_info.st_size / (1024 * 1024),
                            'fecha_modificacion': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                            'es_valido': False  # Lo verificaremos después
                        })
                        
                        print(f"  ✅ Encontrado JSON: {archivo}")
                    except Exception as e:
                        print(f"  ❌ Error procesando {archivo}: {e}")
            
            # Verificar que cada JSON sea válido
            for archivo_info in archivos_json:
                try:
                    with open(archivo_info['ruta'], 'r', encoding='utf-8') as f:
                        json.load(f)  # Intentar cargar para verificar
                    archivo_info['es_valido'] = True
                except json.JSONDecodeError:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = "JSON inválido"
                except Exception as e:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = str(e)
            
            print(f"Total archivos JSON encontrados: {len(archivos_json)}")
            print(f"Archivos JSON válidos: {sum(1 for a in archivos_json if a['es_valido'])}")
            
            return archivos_json
            
        except Exception as e:
            print(f"Error al listar archivos JSON: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def listar_archivos_json_recursivo(ruta_carpeta: str) -> List[Dict]:
        """
        Lista todos los archivos JSON en una carpeta y subcarpetas de forma recursiva
        
        Args:
            ruta_carpeta: Ruta de la carpeta raíz a explorar
            
        Returns:
            Lista de diccionarios con información de cada archivo JSON
        """
        archivos_json = []
        try:
            print(f"Buscando archivos JSON recursivamente en: {ruta_carpeta}")
            
            if not os.path.exists(ruta_carpeta):
                print(f"La carpeta no existe: {ruta_carpeta}")
                return []
            
            # Recorrer todas las carpetas y subcarpetas
            for root, dirs, files in os.walk(ruta_carpeta):
                for archivo in files:
                    if archivo.lower().endswith('.json'):
                        ruta_completa = os.path.join(root, archivo)
                        try:
                            # Obtener información básica del archivo
                            stat_info = os.stat(ruta_completa)
                            fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)
                            
                            # Ruta relativa desde la carpeta base
                            ruta_relativa = os.path.relpath(ruta_completa, ruta_carpeta)
                            
                            archivos_json.append({
                                'nombre': archivo,
                                'ruta_completa': ruta_completa,
                                'ruta_relativa': ruta_relativa,
                                'carpeta': os.path.dirname(ruta_relativa),
                                'tamaño_bytes': stat_info.st_size,
                                'tamaño_mb': stat_info.st_size / (1024 * 1024),
                                'fecha_modificacion': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                                'es_valido': False
                            })
                        except Exception as e:
                            print(f"  ❌ Error procesando {archivo}: {e}")
            
            # Verificar que cada JSON sea válido
            for archivo_info in archivos_json:
                try:
                    with open(archivo_info['ruta_completa'], 'r', encoding='utf-8') as f:
                        json.load(f)
                    archivo_info['es_valido'] = True
                except json.JSONDecodeError:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = "JSON inválido"
                except Exception as e:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = str(e)
            
            print(f"Total archivos JSON encontrados (recursivo): {len(archivos_json)}")
            
            # Mostrar primeros 10 archivos
            for i, archivo in enumerate(archivos_json[:10]):
                estado = "✓" if archivo['es_valido'] else "✗"
                print(f"  {estado} {i+1}. {archivo['ruta_relativa']} ({archivo['tamaño_mb']:.2f} MB)")
            
            if len(archivos_json) > 10:
                print(f"  ... y {len(archivos_json) - 10} más")
            
            return archivos_json
            
        except Exception as e:
            print(f"Error al listar archivos JSON recursivo: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def leer_json(ruta_json: str) -> Dict:
        """
        Lee un archivo JSON y retorna su contenido
        
        Args:
            ruta_json: Ruta del archivo JSON
            
        Returns:
            Diccionario con el contenido del JSON
        """
        try:
            print(f"Leyendo JSON: {ruta_json}")
            
            if not os.path.exists(ruta_json):
                print(f"El archivo no existe: {ruta_json}")
                return {}
            
            with open(ruta_json, 'r', encoding='utf-8') as f:
                contenido = json.load(f)
            
            # Obtener información del archivo
            stat_info = os.stat(ruta_json)
            fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)
            
            print(f"✅ JSON leído correctamente")
            print(f"   Tamaño: {stat_info.st_size} bytes")
            print(f"   Última modificación: {fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Estructura del JSON: {type(contenido)}")
            
            # Si es un diccionario, mostrar algunas claves
            if isinstance(contenido, dict):
                print(f"   Claves principales: {list(contenido.keys())[:5]}")
                if 'links' in contenido:
                    print(f"   Número de links: {len(contenido['links']) if isinstance(contenido['links'], list) else 'N/A'}")
            
            return contenido
            
        except json.JSONDecodeError as e:
            print(f"❌ Error de formato JSON en {ruta_json}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error al leer JSON {ruta_json}: {e}")
            return {}
    
    @staticmethod
    def guardar_json(ruta_json: str, datos: Dict, indent: int = 4) -> bool:
        """
        Guarda datos en un archivo JSON
        
        Args:
            ruta_json: Ruta donde guardar el JSON
            datos: Datos a guardar
            indent: Número de espacios para indentación
            
        Returns:
            True si se guardó correctamente
        """
        try:
            print(f"Guardando JSON en: {ruta_json}")
            
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_json)
            if directorio:
                Funciones.crear_carpeta(directorio)
            
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=indent, ensure_ascii=False)
            
            # Verificar que se guardó correctamente
            if os.path.exists(ruta_json):
                size_bytes = os.path.getsize(ruta_json)
                print(f"✅ JSON guardado correctamente")
                print(f"   Tamaño: {size_bytes} bytes ({size_bytes/1024:.1f} KB)")
                return True
            else:
                print(f"❌ Error: El archivo no se creó")
                return False
                
        except Exception as e:
            print(f"❌ Error al guardar JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def analizar_estructura_json(ruta_json: str) -> Dict:
        """
        Analiza la estructura de un archivo JSON
        
        Args:
            ruta_json: Ruta del archivo JSON
            
        Returns:
            Diccionario con información sobre la estructura del JSON
        """
        try:
            datos = Funciones.leer_json(ruta_json)
            if not datos:
                return {"error": "No se pudo leer el JSON"}
            
            estructura = {
                "tipo": type(datos).__name__,
                "ruta": ruta_json,
                "nombre_archivo": os.path.basename(ruta_json),
                "analisis": {}
            }
            
            if isinstance(datos, dict):
                estructura["analisis"]["tipo"] = "diccionario"
                estructura["analisis"]["num_claves"] = len(datos)
                estructura["analisis"]["claves"] = list(datos.keys())
                
                # Analizar tipos de valores
                tipos_valores = {}
                for clave, valor in datos.items():
                    tipo_valor = type(valor).__name__
                    if tipo_valor not in tipos_valores:
                        tipos_valores[tipo_valor] = []
                    tipos_valores[tipo_valor].append(clave)
                
                estructura["analisis"]["tipos_valores"] = tipos_valores
                
            elif isinstance(datos, list):
                estructura["analisis"]["tipo"] = "lista"
                estructura["analisis"]["num_elementos"] = len(datos)
                
                if datos:
                    # Analizar tipo del primer elemento
                    primer_elemento = datos[0]
                    estructura["analisis"]["tipo_primer_elemento"] = type(primer_elemento).__name__
                    
                    if isinstance(primer_elemento, dict):
                        estructura["analisis"]["claves_primer_elemento"] = list(primer_elemento.keys())
            
            return estructura
            
        except Exception as e:
            print(f"Error analizando estructura JSON: {e}")
            return {"error": str(e)}
    
    # ... (aquí van los otros métodos que ya tienes: descomprimir_zip_local, etc.) ...

    @staticmethod
    def descomprimir_zip_local(ruta_file_zip: str, ruta_descomprimir: str) -> List[Dict]:
        """Descomprime un archivo ZIP y retorna info de archivos"""
        archivos = []
        try:
            with zipfile.ZipFile(ruta_file_zip, 'r') as zip_ref:
                print(f"Descomprimiendo: {ruta_file_zip}")
                print(f"Destino: {ruta_descomprimir}")
                
                # Listar todos los archivos en el ZIP
                zip_info = zip_ref.infolist()
                print(f"Total archivos en ZIP: {len(zip_info)}")
                
                for file_info in zip_info:
                    # Solo procesar archivos (no directorios)
                    if not file_info.is_dir():
                        filename = file_info.filename
                        extension = os.path.splitext(filename)[1].lower()
                        
                        # Solo procesar txt, pdf y json (o todos los archivos para debug)
                        if extension in ['.txt', '.pdf', '.json', '.jpg', '.png', '.docx']:
                            # Extraer el archivo
                            zip_ref.extract(file_info, ruta_descomprimir)
                            
                            # Ruta completa del archivo extraído
                            ruta_completa = os.path.join(ruta_descomprimir, filename)
                            
                            # Obtener información de la estructura de carpetas
                            carpeta_relativa = os.path.dirname(filename)
                            carpeta_destino = carpeta_relativa if carpeta_relativa else 'raiz'
                            
                            nombre_archivo = os.path.basename(filename)
                            
                            archivos.append({
                                'carpeta': carpeta_destino,
                                'nombre': nombre_archivo,
                                'ruta': ruta_completa,
                                'extension': extension.replace('.', ''),
                                'tamaño_bytes': os.path.getsize(ruta_completa) if os.path.exists(ruta_completa) else 0
                            })
                            
                            print(f"  ✓ Extraído: {nombre_archivo} ({extension})")
                
                print(f"Archivos extraídos: {len(archivos)}")
                return archivos
                
        except Exception as e:import os
import zipfile
import requests
import json
import PyPDF2
from PIL import Image
import pytesseract
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil

class Funciones:
    @staticmethod
    def crear_carpeta(ruta: str) -> bool:
        """Crea una carpeta si no existe"""
        try:
            if not os.path.exists(ruta):
                os.makedirs(ruta)
                print(f"Carpeta creada: {ruta}")
            return True
        except Exception as e:
            print(f"Error al crear carpeta: {e}")
            return False

    @staticmethod
    def borrar_contenido_carpeta(ruta: str) -> bool:
        """
        Borra el contenido de una carpeta sin eliminar la carpeta misma

        Args:
            ruta: Ruta de la carpeta a limpiar

        Returns:
            True si se borró correctamente, False en caso de error
        """
        try:
            if not os.path.exists(ruta):
                return True  # Si no existe, no hay nada que borrar

            if not os.path.isdir(ruta):
                return False  # No es una carpeta

            # Eliminar todos los archivos y subcarpetas dentro
            for item in os.listdir(ruta):
                item_path = os.path.join(ruta, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Eliminar archivo o enlace simbólico
                        print(f"  Eliminado archivo: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Eliminar directorio y su contenido
                        print(f"  Eliminado directorio: {item_path}")
                except Exception as e:
                    print(f"Error al eliminar {item_path}: {e}")
                    return False

            return True
        except Exception as e:
            print(f"Error al borrar contenido de carpeta: {e}")
            return False

    @staticmethod
    def listar_archivos_json(ruta_carpeta: str) -> List[Dict]:
        """
        Lista todos los archivos JSON en una carpeta

        Args:
            ruta_carpeta: Ruta de la carpeta a explorar

        Returns:
            Lista de diccionarios con información de cada archivo JSON
        """
        archivos_json = []
        try:
            print(f"Buscando archivos JSON en: {ruta_carpeta}")

            if not os.path.exists(ruta_carpeta):
                print(f"La carpeta no existe: {ruta_carpeta}")
                return []

            for archivo in os.listdir(ruta_carpeta):
                ruta_completa = os.path.join(ruta_carpeta, archivo)

                if os.path.isfile(ruta_completa) and archivo.lower().endswith('.json'):
                    try:
                        stat_info = os.stat(ruta_completa)
                        fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)

                        archivos_json.append({
                            'nombre': archivo,
                            'ruta': ruta_completa,
                            'tamaño_bytes': stat_info.st_size,
                            'tamaño_mb': stat_info.st_size / (1024 * 1024),
                            'fecha_modificacion': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                            'es_valido': False
                        })
                    except Exception as e:
                        print(f"  ❌ Error procesando {archivo}: {e}")

            # Verificar que cada JSON sea válido
            for archivo_info in archivos_json:
                try:
                    with open(archivo_info['ruta'], 'r', encoding='utf-8') as f:
                        json.load(f)
                    archivo_info['es_valido'] = True
                except json.JSONDecodeError:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = "JSON inválido"
                except Exception as e:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = str(e)

            print(f"Total archivos JSON encontrados: {len(archivos_json)}")
            return archivos_json

        except Exception as e:
            print(f"Error al listar archivos JSON: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def listar_archivos_json_recursivo(ruta_carpeta: str) -> List[Dict]:
        """
        Lista todos los archivos JSON en una carpeta y subcarpetas de forma recursiva

        Args:
            ruta_carpeta: Ruta de la carpeta raíz a explorar

        Returns:
            Lista de diccionarios con información de cada archivo JSON
        """
        archivos_json = []
        try:
            print(f"Buscando archivos JSON recursivamente en: {ruta_carpeta}")

            if not os.path.exists(ruta_carpeta):
                print(f"La carpeta no existe: {ruta_carpeta}")
                return []

            for root, dirs, files in os.walk(ruta_carpeta):
                for archivo in files:
                    if archivo.lower().endswith('.json'):
                        ruta_completa = os.path.join(root, archivo)
                        try:
                            stat_info = os.stat(ruta_completa)
                            fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)

                            ruta_relativa = os.path.relpath(ruta_completa, ruta_carpeta)

                            archivos_json.append({
                                'nombre': archivo,
                                'ruta_completa': ruta_completa,
                                'ruta_relativa': ruta_relativa,
                                'carpeta': os.path.dirname(ruta_relativa),
                                'tamaño_bytes': stat_info.st_size,
                                'tamaño_mb': stat_info.st_size / (1024 * 1024),
                                'fecha_modificacion': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                                'es_valido': False
                            })
                        except Exception as e:
                            print(f"  ❌ Error procesando {archivo}: {e}")

            # Verificar que cada JSON sea válido
            for archivo_info in archivos_json:
                try:
                    with open(archivo_info['ruta_completa'], 'r', encoding='utf-8') as f:
                        json.load(f)
                    archivo_info['es_valido'] = True
                except json.JSONDecodeError:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = "JSON inválido"
                except Exception as e:
                    archivo_info['es_valido'] = False
                    archivo_info['error'] = str(e)

            print(f"Total archivos JSON encontrados (recursivo): {len(archivos_json)}")
            return archivos_json

        except Exception as e:
            print(f"Error al listar archivos JSON recursivo: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def leer_json(ruta_json: str) -> Dict:
        """
        Lee un archivo JSON y retorna su contenido

        Args:
            ruta_json: Ruta del archivo JSON

        Returns:
            Diccionario con el contenido del JSON
        """
        try:
            print(f"Leyendo JSON: {ruta_json}")

            if not os.path.exists(ruta_json):
                print(f"El archivo no existe: {ruta_json}")
                return {}

            with open(ruta_json, 'r', encoding='utf-8') as f:
                contenido = json.load(f)

            return contenido

        except json.JSONDecodeError as e:
            print(f"❌ Error de formato JSON en {ruta_json}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error al leer JSON {ruta_json}: {e}")
            return {}

    @staticmethod
    def guardar_json(ruta_json: str, datos: Dict, indent: int = 4) -> bool:
        """
        Guarda datos en un archivo JSON

        Args:
            ruta_json: Ruta donde guardar el JSON
            datos: Datos a guardar
            indent: Número de espacios para indentación

        Returns:
            True si se guardó correctamente
        """
        try:
            print(f"Guardando JSON en: {ruta_json}")

            directorio = os.path.dirname(ruta_json)
            if directorio:
                Funciones.crear_carpeta(directorio)

            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=indent, ensure_ascii=False)

            if os.path.exists(ruta_json):
                return True
            else:
                print(f"❌ Error: El archivo no se creó")
                return False

        except Exception as e:
            print(f"❌ Error al guardar JSON: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def analizar_estructura_json(ruta_json: str) -> Dict:
        """
        Analiza la estructura de un archivo JSON

        Args:
            ruta_json: Ruta del archivo JSON

        Returns:
            Diccionario con información sobre la estructura del JSON
        """
        try:
            datos = Funciones.leer_json(ruta_json)
            if not datos:
                return {"error": "No se pudo leer el JSON"}

            estructura = {
                "tipo": type(datos).__name__,
                "ruta": ruta_json,
                "nombre_archivo": os.path.basename(ruta_json),
                "analisis": {}
            }

            if isinstance(datos, dict):
                estructura["analisis"]["tipo"] = "diccionario"
                estructura["analisis"]["num_claves"] = len(datos)
                estructura["analisis"]["claves"] = list(datos.keys())

                tipos_valores = {}
                for clave, valor in datos.items():
                    tipo_valor = type(valor).__name__
                    if tipo_valor not in tipos_valores:
                        tipos_valores[tipo_valor] = []
                    tipos_valores[tipo_valor].append(clave)

                estructura["analisis"]["tipos_valores"] = tipos_valores

            elif isinstance(datos, list):
                estructura["analisis"]["tipo"] = "lista"
                estructura["analisis"]["num_elementos"] = len(datos)

                if datos:
                    primer_elemento = datos[0]
                    estructura["analisis"]["tipo_primer_elemento"] = type(primer_elemento).__name__

                    if isinstance(primer_elemento, dict):
                        estructura["analisis"]["claves_primer_elemento"] = list(primer_elemento.keys())

            return estructura

        except Exception as e:
            print(f"Error analizando estructura JSON: {e}")
            return {"error": str(e)}

    @staticmethod
    def descomprimir_zip_local(ruta_file_zip: str, ruta_descomprimir: str) -> List[Dict]:
        """Descomprime un archivo ZIP y retorna info de archivos"""
        archivos = []
        try:
            with zipfile.ZipFile(ruta_file_zip, 'r') as zip_ref:
                print(f"Descomprimiendo: {ruta_file_zip}")
                print(f"Destino: {ruta_descomprimir}")

                zip_info = zip_ref.infolist()
                print(f"Total archivos en ZIP: {len(zip_info)}")

                for file_info in zip_info:
                    if not file_info.is_dir():
                        filename = file_info.filename
                        extension = os.path.splitext(filename)[1].lower()

                        if extension in ['.txt', '.pdf', '.json', '.jpg', '.png', '.docx']:
                            zip_ref.extract(file_info, ruta_descomprimir)

                            ruta_completa = os.path.join(ruta_descomprimir, filename)

                            carpeta_relativa = os.path.dirname(filename)
                            carpeta_destino = carpeta_relativa if carpeta_relativa else 'raiz'

                            nombre_archivo = os.path.basename(filename)

                            archivos.append({
                                'carpeta': carpeta_destino,
                                'nombre': nombre_archivo,
                                'ruta': ruta_completa,
                                'extension': extension.replace('.', ''),
                                'tamaño_bytes': os.path.getsize(ruta_completa) if os.path.exists(ruta_completa) else 0
                            })

                print(f"Archivos extraídos: {len(archivos)}")
                return archivos

        except Exception as e:
            print(f"Error al descomprimir ZIP: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def descargar_y_descomprimir_zip(url: str, carpeta_destino: str, tipoArchivo: str = '') -> List[Dict]:
        """Descarga y descomprime un ZIP desde URL"""
        try:
            Funciones.crear_carpeta(carpeta_destino)

            response = requests.get(url, stream=True)
            zip_path = os.path.join(carpeta_destino, 'temp.zip')

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            archivos = Funciones.descomprimir_zip_local(zip_path, carpeta_destino)

            os.remove(zip_path)

            return archivos
        except Exception as e:
            print(f"Error al descargar y descomprimir: {e}")
            return []

    @staticmethod
    def allowed_file(filename: str, extensions: List[str]) -> bool:
        """Verifica si un archivo tiene extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

    @staticmethod
    def extraer_texto_pdf(ruta_pdf: str) -> str:
        """
        Extrae texto de un archivo PDF

        Args:
            ruta_pdf: Ruta del archivo PDF

        Returns:
            Texto extraído del PDF
        """
        try:
            texto = ""
            with open(ruta_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    texto += page.extract_text() + "\n"
            return texto.strip()
        except Exception as e:
            print(f"Error al extraer texto del PDF {ruta_pdf}: {e}")
            return ""

    @staticmethod
    def extraer_texto_pdf_ocr(ruta_pdf: str) -> str:
        """
        Extrae texto de un PDF usando OCR (útil para PDFs escaneados)

        Args:
            ruta_pdf: Ruta del archivo PDF

        Returns:
            Texto extraído usando OCR
        """
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(ruta_pdf)

            texto = ""
            for i, image in enumerate(images):
                texto += pytesseract.image_to_string(image, lang='spa') + "\n"

            return texto.strip()
        except Exception as e:
            print(f"Error al extraer texto con OCR del PDF {ruta_pdf}: {e}")
            return ""

    @staticmethod
    def listar_archivos_carpeta(ruta_carpeta: str, extensiones: List[str] = None) -> List[Dict]:
        """
        Lista archivos en una carpeta con extensiones específicas

        Args:
            ruta_carpeta: Ruta de la carpeta
            extensiones: Lista de extensiones a filtrar (ej: ['pdf', 'txt'])

        Returns:
            Lista de diccionarios con información de archivos
        """
        archivos = []
        try:
            if not os.path.exists(ruta_carpeta):
                return []

            for archivo in os.listdir(ruta_carpeta):
                ruta_completa = os.path.join(ruta_carpeta, archivo)
                if os.path.isfile(ruta_completa):
                    extension = os.path.splitext(archivo)[1].lower().replace('.', '')

                    if extensiones is None or extension in extensiones:
                        archivos.append({
                            'nombre': archivo,
                            'ruta': ruta_completa,
                            'extension': extension,
                            'tamaño': os.path.getsize(ruta_completa)
                        })

            return archivos
        except Exception as e:
            print(f"Error al listar archivos: {e}")
            return []
            print(f"Error al descomprimir ZIP: {e}")
            import traceback
            traceback.print_exc()
            return []