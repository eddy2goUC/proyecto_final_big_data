# Proyecto Final - Big Data (Tercer Semestre Maestría)

**Aplicación Web para Gestión, Búsqueda y Análisis de Documentos con Big Data**

---

## 📋 Descripción General

Esta aplicación web integra tecnologías de **Big Data** para gestionar, procesar y analizar documentos. Combina **MongoDB** para almacenamiento de metadatos y usuarios, **Elasticsearch** para búsqueda full-text escalable, y **PLN (Procesamiento de Lenguaje Natural)** para análisis avanzado de contenidos. La aplicación permite:

- **Gestión de usuarios** con roles y permisos
- **Ingesta de documentos** desde URLs (descarga de ZIP con archivos PDF/TXT)
- **Búsqueda inteligente** en Elasticsearch con agregaciones
- **Análisis de texto** usando NLP (entidades, similitud, resumen)
- **Web scraping** para extracción automática de documentos
- **Panel administrativo** para gestionar usuarios, documentos e índices

---

## 🏗️ Arquitectura del Proyecto

### Componentes Principales

```
proyecto_final_big_data/
├── app.py                      # Aplicación Flask (punto de entrada)
├── Helpers/                    # Módulos de lógica de negocio
│   ├── funciones.py            # Utilidades: descarga ZIP, manejo de archivos
│   ├── mongoDB.py              # Wrapper para MongoDB (CRUD usuarios)
│   ├── elastic.py              # Cliente Elasticsearch (búsqueda y índices)
│   ├── PLN.py                  # Procesamiento de Lenguaje Natural (spaCy, transformers)
│   ├── webScraping.py          # Web scraping y extracción de links
│   └── __init__.py             # Exporta las clases principales
├── templates/                  # Plantillas HTML (Jinja2)
│   ├── landing.html            # Página principal pública
│   ├── buscador.html           # Búsqueda de documentos
│   ├── login.html              # Autenticación
│   ├── admin.html              # Panel administrativo
│   ├── gestor_usuarios.html    # Gestión de usuarios
│   ├── gestor_elastic.html     # Gestión de índices Elasticsearch
│   └── ...
├── static/                     # Assets estáticos
│   ├── css/                    # Estilos (gestor.css, landingPage.css)
│   ├── js/                     # JavaScript (main.js, AJAX)
│   └── uploads/                # Carpeta de subidas
└── requirements.txt            # Dependencias Python
```

### Flujo de Datos

```
Usuario (Web) 
    ↓
Flask (app.py) ← rutas, templates, lógica
    ↓
Helpers/
    ├→ MongoDB: autenticación, permisos, metadatos
    ├→ ElasticSearch: indexación y búsqueda full-text
    ├→ Funciones: descarga, descompresión, manejo archivos
    ├→ PLN: análisis texto, entidades, similitud
    └→ WebScraping: extracción automática de documentos
    ↓
Bases de datos (MongoDB + Elasticsearch)
```

---

## 🔧 Tecnologías y Dependencias

| Componente | Propósito |
|-----------|-----------|
| **Flask** | Framework web (rutas, templates, sesiones) |
| **MongoDB** | Base de datos NoSQL (usuarios, roles, metadatos) |
| **Elasticsearch** | Motor de búsqueda full-text y análisis |
| **spaCy** | NLP: reconocimiento de entidades, POS tagging |
| **SentenceTransformers** | Embeddings multilingual para similitud |
| **transformers (Hugging Face)** | Pipelines de PLN avanzado |
| **BeautifulSoup + Requests** | Web scraping |
| **pandas, numpy** | Análisis de datos |
| **python-dotenv** | Gestión de variables de entorno |
| **bcrypt** | Encriptación de contraseñas |

---

## 📦 Funcionalidades Clave

### 1. **Gestión de Usuarios** (`Helpers/mongoDB.py`)
- Crear, leer, actualizar y eliminar usuarios
- Autenticación con MD5 (nota: considerar migración a bcrypt)
- Asignación de roles y permisos
- Validación contra MongoDB

```python
from Helpers.mongoDB import MongoDB
db = MongoDB(uri="mongodb://...", db_name="proyecto")
usuario = db.validar_usuario("admin", "password123", "usuarios")
```

### 2. **Ingesta de Documentos** (`Helpers/funciones.py`)
- Descarga de archivos ZIP desde URL
- Descompresión selectiva (filtra solo `.txt` y `.pdf`)
- Retorna metadatos: `carpeta`, `nombre`, `ruta`, `extension`

```python
from Helpers.funciones import Funciones
archivos = Funciones.descargar_y_descomprimir_zip(
    url="https://ejemplo.com/docs.zip",
    carpeta_destino="static/uploads/"
)
# Retorna: [{'carpeta': 'docs', 'nombre': 'file.pdf', 'ruta': '...', 'extension': '.pdf'}, ...]
```

### 3. **Búsqueda Elasticsearch** (`Helpers/elastic.py`)
- Indexación de documentos
- Búsqueda full-text por campo (titulo, contenido, autor)
- Agregaciones: documentos por mes, por autor
- Gestión de índices

```python
from Helpers.elastic import ElasticSearch
elastic = ElasticSearch(cloud_url="https://...", api_key="...")
resultados = elastic.buscar(index="proyecto_big_data", texto="machine learning")
```

### 4. **Procesamiento de Lenguaje Natural** (`Helpers/PLN.py`)
- Extracción de entidades (personas, lugares, organizaciones, fechas)
- Análisis de similitud entre textos
- Cálculo de TF-IDF
- Resumen automático de documentos
- Análisis de sentimientos

```python
from Helpers.PLN import PLN
pln = PLN()
entidades = pln.extraer_entidades("Juan Pérez trabajó en Google en 2023")
# Retorna: {'personas': ['Juan Pérez'], 'organizaciones': ['Google'], ...}
```

### 5. **Web Scraping** (`Helpers/webScraping.py`)
- Extracción automática de links de libros/documentos
- Filtrado por tipo de archivo (PDF, TXT, etc.)
- Descargar y procesar masivamente

```python
from Helpers.webScraping import WebScraping
scraper = WebScraping(dominio_base="https://infolibros.org/")
libros = scraper.extract_links("https://infolibros.org/libros-pdf-gratis/")
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- MongoDB local o cloud (Atlas)
- Elasticsearch Cloud (API Key)
- git

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/eddy2goUC/proyecto_final_big_data.git
   cd proyecto_final_big_data
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # o
   source .venv/bin/activate   # macOS/Linux
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Descargar modelos de PLN** (primera vez, puede tardar)
   ```bash
   python -m spacy download es_core_news_lg
   ```

5. **Configurar variables de entorno** (crear `.env`)
   ```env
   MONGO_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net
   MONGO_DB=proyecto_big_data
   MONGO_COLECCION=usuarios
   
   ELASTIC_CLOUD_URL=https://xxxxx.es.us-central1.gcp.cloud.es.io
   ELASTIC_API_KEY=VXNlcjpQYXNzd29yZA==
   ELASTIC_INDEX_DEFAULT=proyecto_big_data
   
   SECRET_KEY=tu_clave_secreta_muy_segura_123456
   ```

6. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```
   Acceder en: `http://localhost:5000`

---

## 📖 Rutas Principales de la API

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Página de inicio (landing page) |
| `/about` | GET | Página informativa |
| `/buscador` | GET | Interfaz de búsqueda |
| `/buscar-elastic` | POST | API de búsqueda (JSON) |
| `/login` | GET/POST | Autenticación de usuarios |
| `/admin` | GET | Panel administrativo (requiere login) |
| `/gestor-usuarios` | GET/POST | CRUD de usuarios (admin) |
| `/gestor-elastic` | GET/POST | Gestión de índices (admin) |

---

## 📐 Patrones y Convenciones

### Manejo de Errores
Todos los helpers retornan valores seguros en caso de error:
```python
# Funciones.py: retorna [] si falla
# mongoDB.py: retorna None o False
# elastic.py: retorna {'success': False, 'error': 'msg'}
```

### Logging
Se usan `print()` para debugging. Para logs en producción, considerar agregar `logging` module.

### Autenticación
- Usuario/contraseña validados contra MongoDB
- Sesiones Flask con `session['usuario']`
- Permisos basados en roles (usuario, admin)

---

## 🔐 Consideraciones de Seguridad

⚠️ **IMPORTANTE:**
- Actualmente se usa **MD5 para hashing de contraseñas** (`mongoDB.py`). Esto es **débil** para producción.
- **Recomendación:** Migrar a `bcrypt` o `argon2` con plan de migración para usuarios existentes.
- **Secretos:** Usar `.env` y NUNCA commitear a git.
- **CORS:** Implementar si se necesita acceso desde otros dominios.

---

## 📝 Notas para Desarrolladores

1. **Agregar nuevos helpers:** Crear clase en `Helpers/` y exportar en `__init__.py`
2. **Templates:** Usar Jinja2 con `base.html` como plantilla base
3. **Assets estáticos:** Colocar en `static/css/` y `static/js/`
4. **Variables de entorno:** No hardcodear; usar `os.getenv()`

---

## 🎯 Roadmap Futuro

- [ ] Migración de MD5 a bcrypt
- [ ] Tests unitarios y de integración
- [ ] API REST documentada (OpenAPI/Swagger)
- [ ] Docker y docker-compose
- [ ] Caché con Redis
- [ ] Procesamiento batch/asincrónico (Celery)
- [ ] Dashboard de analytics

---

## 👨‍💻 Autor

- **Nombre:** Eddy2Go  
- **Institución:** Universidad Central - Maestría en Analítica  
- **Materia:** Big Data - Tercer Semestre  
- **Año:** 2025

---

## 📄 Licencia

Este proyecto es académico. Consulta con el profesor para permisos de distribución.

---

## 🤝 Contribuciones

Para reportar bugs o sugerir mejoras, abre un issue o contacta al autor.