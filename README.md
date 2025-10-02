## Descripción del Proyecto
Sistema de facturación electrónica simulado que emula el proceso de facturación de la AFIP (Administración Federal de Ingresos Públicos) de Argentina. Permite generar facturas tipo A y B con autorización CAE simulada.

### Características Principales
#### Frontend (HTML/CSS/JavaScript)
Interfaz moderna y responsive con diseño gradient

Gestión de facturas tipo A y B

Cálculo automático de subtotales, IVA y totales

Listado de facturas emitidas con detalles completos

Generación de PDF para impresión y descarga

Validación en tiempo real de formularios

Estado de conexión con el servidor backend

#### Backend (Python/Flask)
API RESTful para gestión de facturas

Generación de CAE simulado (Código de Autorización Electrónico)

Numeración automática de facturas con formato XXXXX-XXXXXXXX

Cálculo de impuestos según tipo de factura

Generación de PDF con ReportLab y FPDF

Base de datos en memoria para almacenamiento temporal

Endpoints para estadísticas y verificación de CAE

### Tecnologías Utilizadas
#### Frontend
HTML5 - Estructura semántica

CSS3 - Estilos con gradients y diseño moderno

JavaScript ES6+ - Lógica de aplicación

jsPDF - Generación de PDFs en cliente

html2canvas - Captura de pantalla para PDF

#### Backend
Python 3.x - Lenguaje de programación

Flask - Framework web

Flask-CORS - Manejo de CORS

ReportLab - Generación avanzada de PDF

FPDF - Generación simple de PDF

### Instalación y Configuración
Prerrequisitos
Python 3.7 o superior

pip (gestor de paquetes de Python)

Navegador web moderno

## Pasos de Instalación
Clonar el repositorio

bash
git clone [url-del-repositorio]
cd sistema-facturacion-afip
Instalar dependencias de Python

bash
pip install -r requirements.txt
Ejecutar el servidor backend

bash
python app.py
Abrir el frontend

Abrir index.html en un navegador web

O servir mediante un servidor local:

bash
python -m http.server 8000
Estructura de Archivos
text
sistema-facturacion/
├── index.html          # Frontend principal
├── app.py             # Backend Flask
├── requirements.txt   # Dependencias Python
└── README.md         # Documentación
## Endpoints de la API
### Facturas
POST /api/facturas - Crear nueva factura

GET /api/facturas - Obtener todas las facturas

GET /api/facturas/<id> - Obtener factura por ID

GET /api/facturas/<id>/pdf - Generar PDF de factura

GET /api/facturas/<id>/pdf-simple - Generar PDF simple

### Utilidades
GET /api/puntos-venta - Obtener puntos de venta

GET /api/verificar-cae/<cae> - Verificar validez de CAE

GET /api/estadisticas - Obtener estadísticas

## Tipos de Factura
### Factura A
Para: Responsables Inscriptos

IVA: Discriminado (21%)

Formato: XXXXX-XXXXXXXX

Características: Muestra IVA por separado

### Factura B
Para: Consumidores Finales

IVA: Incluido en el precio

Formato: XXXXX-XXXXXXXX

Características: No muestra IVA por separado

## Mejoras Futuras
Base de datos persistente (SQLite/PostgreSQL)

Autenticación de usuarios

Roles y permisos

Exportación a Excel

Integración con AFIP real

Notificaciones por email

Dashboard con gráficos

API documentation con Swagger

## Contribución
Fork del proyecto

Crear rama para feature (git checkout -b feature/AmazingFeature)

Commit de cambios (git commit -m 'Add AmazingFeature')

Push a la rama (git push origin feature/AmazingFeature)

Abrir Pull Request

📄 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## Soporte
Para soporte y consultas:

Abrir un issue en el repositorio

Contactar al equipo de desarrollo

Revisar la documentación técnica

Nota: Este es un sistema de simulación para fines educativos y de desarrollo. No debe utilizarse para facturación real sin las debidas autorizaciones de AFIP.
