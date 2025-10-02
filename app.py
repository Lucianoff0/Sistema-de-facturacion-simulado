# app.py - Backend Sistema de Facturación AFIP/ARCA con Flask
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from fpdf import FPDF
import base64

app = Flask(__name__)
CORS(app)

# Base de datos simulada
facturas = []
contadores = {'A': 1, 'B': 1}
puntos_venta = [1, 2, 3, 4, 5]

def generar_cae():
    """Generar CAE simulado (Código de Autorización Electrónico)"""
    return str(random.randint(10000000000000, 99999999999999))

def generar_numero_factura(tipo, punto_venta):
    """Generar número de factura con formato XXXXX-XXXXXXXX"""
    global contadores
    numero = contadores[tipo]
    contadores[tipo] += 1
    return f"{str(punto_venta).zfill(5)}-{str(numero).zfill(8)}"


def calcular_totales(items, tipo):
    importe_iva = 0.21
    """Calcular subtotal, IVA y total según tipo de factura"""
    subtotal = sum(item['cantidad'] * item['precioUnitario'] for item in items)
    
    if tipo == 'A':
        # Factura A: discrimina IVA
        iva = subtotal * importe_iva
        total = subtotal + iva
        return {
            'subtotal': round(subtotal, 2),
            'iva': round(iva, 2),
            'total': round(total, 2)
        }
    else:
        # Factura B: IVA incluido
        total = subtotal + (subtotal * importe_iva)
        subtotal_neto = total   
        iva = total - subtotal_neto
       
        return {
            'subtotal': round(subtotal_neto, 2),
            'iva': round(iva, 2),
            'total': round(total, 2) 
        }


@app.route('/api/facturas', methods=['POST'])
def crear_factura():
    """Crear nueva factura"""
    try:
        data = request.get_json()
        
        tipo = data.get('tipo')
        punto_venta = data.get('puntoVenta')
        cliente = data.get('cliente')
        items = data.get('items')
        
        # Validaciones
        if tipo not in ['A', 'B']:
            return jsonify({'error': 'Tipo de factura inválido. Debe ser A o B'}), 400
        
        if punto_venta not in puntos_venta:
            return jsonify({'error': 'Punto de venta inválido'}), 400
        
        if not items or len(items) == 0:
            return jsonify({'error': 'Debe incluir al menos un item'}), 400
        
        # Generar factura
        totales = calcular_totales(items, tipo)
        fecha = datetime.now()
        
        factura = {
            'id': len(facturas) + 1,
            'tipo': tipo,
            'numero': generar_numero_factura(tipo, punto_venta),
            'puntoVenta': punto_venta,
            'cae': generar_cae(),
            'fechaEmision': fecha.isoformat(),
            'fechaVencimientoCAE': (fecha + timedelta(days=10)).isoformat(),
            'cliente': cliente,
            'items': items,
            'subtotal': totales['subtotal'],
            'iva': totales['iva'],
            'total': totales['total'],
            'estado': 'Autorizada'
        }
        
        facturas.append(factura)
        
        return jsonify({
            'success': True,
            'mensaje': 'Factura autorizada correctamente',
            'factura': factura
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al procesar la factura: {str(e)}'}), 500

@app.route('/api/facturas', methods=['GET'])
def obtener_facturas():
    """Obtener todas las facturas con filtros opcionales"""
    tipo = request.args.get('tipo')
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    
    resultado = facturas.copy()
    
    if tipo:
        resultado = [f for f in resultado if f['tipo'] == tipo]
    
    if desde:
        fecha_desde = datetime.fromisoformat(desde)
        resultado = [f for f in resultado if datetime.fromisoformat(f['fechaEmision']) >= fecha_desde]
    
    if hasta:
        fecha_hasta = datetime.fromisoformat(hasta)
        resultado = [f for f in resultado if datetime.fromisoformat(f['fechaEmision']) <= fecha_hasta]
    
    return jsonify({
        'total': len(resultado),
        'facturas': resultado
    })

@app.route('/api/facturas/<int:id>', methods=['GET'])
def obtener_factura(id):
    """Obtener factura por ID"""
    factura = next((f for f in facturas if f['id'] == id), None)
    
    if not factura:
        return jsonify({'error': 'Factura no encontrada'}), 404
    
    return jsonify(factura)

@app.route('/api/puntos-venta', methods=['GET'])
def obtener_puntos_venta():
    """Obtener puntos de venta disponibles"""
    return jsonify(puntos_venta)

@app.route('/api/verificar-cae/<cae>', methods=['GET'])
def verificar_cae(cae):
    """Verificar validez de un CAE"""
    factura = next((f for f in facturas if f['cae'] == cae), None)
    
    if not factura:
        return jsonify({
            'valido': False,
            'mensaje': 'CAE no encontrado'
        })
    
    vencido = datetime.now() > datetime.fromisoformat(factura['fechaVencimientoCAE'])
    
    return jsonify({
        'valido': not vencido,
        'factura': factura,
        'mensaje': 'CAE vencido' if vencido else 'CAE válido'
    })

@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtener estadísticas generales"""
    total_facturado = sum(f['total'] for f in facturas)
    facturas_a = len([f for f in facturas if f['tipo'] == 'A'])
    facturas_b = len([f for f in facturas if f['tipo'] == 'B'])
    
    return jsonify({
        'totalFacturas': len(facturas),
        'facturasA': facturas_a,
        'facturasB': facturas_b,
        'totalFacturado': round(total_facturado, 2)
    })

@app.route('/', methods=['GET'])
def index():
    """Página de bienvenida"""
    return '''
    <h1>Sistema de Facturación AFIP/ARCA</h1>
    <p>API REST para facturación electrónica simulada</p>
    <h2>Endpoints disponibles:</h2>
    <ul>
        <li>POST /api/facturas - Crear nueva factura</li>
        <li>GET /api/facturas - Obtener todas las facturas</li>
        <li>GET /api/facturas/:id - Obtener factura por ID</li>
        <li>GET /api/puntos-venta - Obtener puntos de venta</li>
        <li>GET /api/verificar-cae/:cae - Verificar CAE</li>
        <li>GET /api/estadisticas - Obtener estadísticas</li>
    </ul>
    '''

if __name__ == '__main__':
    print('🚀 Servidor AFIP/ARCA corriendo en http://localhost:5000')
    print('📋 Endpoints disponibles:')
    print('   POST   /api/facturas')
    print('   GET    /api/facturas')
    print('   GET    /api/facturas/:id')
    print('   GET    /api/puntos-venta')
    print('   GET    /api/verificar-cae/:cae')
    print('   GET    /api/estadisticas')
    app.run(host="0.0.0.0", debug=True, port=5000)

@app.route('/api/facturas/<int:id>/pdf', methods=['GET'])
def generar_pdf_factura(id):
    """Generar PDF de una factura"""
    try:
        factura = next((f for f in facturas if f['id'] == id), None)
        
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        # Crear PDF con reportlab
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Configuración
        c.setFont("Helvetica-Bold", 16)
        
        # Encabezado
        c.drawString(50, height - 50, "MI EMPRESA S.A.")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, "CUIT: 30-12345678-9")
        c.drawString(50, height - 85, "Dirección: Av. Principal 1234, CABA")
        c.drawString(50, height - 100, "Teléfono: +54 11 1234-5678")
        c.drawString(50, height - 115, "IVA: Responsable Inscripto")
        
        # Información de la factura
        c.setFont("Helvetica-Bold", 20)
        c.drawString(300, height - 50, f"FACTURA {factura['tipo']}")
        c.setFont("Helvetica", 10)
        c.drawString(300, height - 70, f"Número: {factura['numero']}")
        c.drawString(300, height - 85, f"Fecha: {datetime.fromisoformat(factura['fechaEmision']).strftime('%d/%m/%Y')}")
        c.drawString(300, height - 100, f"Punto Venta: {factura['puntoVenta']}")
        
        # Datos del cliente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 140, "DATOS DEL CLIENTE")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 160, f"Razón Social: {factura['cliente']['razonSocial']}")
        c.drawString(50, height - 175, f"CUIT: {factura['cliente'].get('cuit', 'N/D')}")
        c.drawString(50, height - 190, f"Domicilio: {factura['cliente'].get('domicilio', 'N/D')}")
        c.drawString(50, height - 205, f"Condición IVA: {factura['cliente']['condicionIVA']}")
        
        # Items de la factura
        y_position = height - 240
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "Descripción")
        c.drawString(300, y_position, "Cant.")
        c.drawString(350, y_position, "Precio Unit.")
        c.drawString(450, y_position, "Subtotal")
        
        y_position -= 20
        c.setFont("Helvetica", 9)
        
        for item in factura['items']:
            if y_position < 100:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 9)
            
            # Descripción (con wrap text si es muy largo)
            descripcion = item['descripcion']
            if len(descripcion) > 40:
                descripcion = descripcion[:37] + "..."
            
            c.drawString(50, y_position, descripcion)
            c.drawString(300, y_position, str(item['cantidad']))
            c.drawString(350, y_position, f"${item['precioUnitario']:.2f}")
            c.drawString(450, y_position, f"${item['cantidad'] * item['precioUnitario']:.2f}")
            y_position -= 15
        
        # Totales
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y_position, "SUBTOTAL:")
        c.drawString(450, y_position, f"${factura['subtotal']:.2f}")
        
        y_position -= 15
        c.drawString(350, y_position, "IVA (21%):")
        c.drawString(450, y_position, f"${factura['iva']:.2f}")
        
        y_position -= 20
        c.setFont("Helvetica-Bold", 16)
        c.drawString(350, y_position, "TOTAL:")
        c.drawString(450, y_position, f"${factura['total']:.2f}")
        
        # Información CAE
        y_position -= 40
        c.setFont("Helvetica", 8)
        c.drawString(50, y_position, f"CAE: {factura['cae']}")
        c.drawString(50, y_position - 12, f"Fecha Vto. CAE: {datetime.fromisoformat(factura['fechaVencimientoCAE']).strftime('%d/%m/%Y')}")
        c.drawString(50, y_position - 24, f"Estado: {factura['estado']}")
        
        c.save()
        
        buffer.seek(0)
        
        return buffer.getvalue(), 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=factura_{factura["numero"]}.pdf'
        }
        
    except Exception as e:
        return jsonify({'error': f'Error al generar PDF: {str(e)}'}), 500

# Versión alternativa con FPDF (más simple)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'MI EMPRESA S.A.', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'CUIT: 30-12345678-9', 0, 1, 'L')
        self.cell(0, 5, 'Dirección: Av. Principal 1234, CABA', 0, 1, 'L')
        self.cell(0, 5, 'Teléfono: +54 11 1234-5678', 0, 1, 'L')
        self.ln(10)

@app.route('/api/facturas/<int:id>/pdf-simple', methods=['GET'])
def generar_pdf_simple(id):
    """Generar PDF simple usando FPDF"""
    try:
        factura = next((f for f in facturas if f['id'] == id), None)
        
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        pdf = PDF()
        pdf.add_page()
        
        # Información de la factura
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, f'FACTURA {factura["tipo"]}', 0, 1, 'R')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Número: {factura["numero"]}', 0, 1, 'R')
        pdf.cell(0, 8, f'Fecha: {datetime.fromisoformat(factura["fechaEmision"]).strftime("%d/%m/%Y")}', 0, 1, 'R')
        
        pdf.ln(10)
        
        # Datos del cliente
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'DATOS DEL CLIENTE', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Razón Social: {factura["cliente"]["razonSocial"]}', 0, 1)
        pdf.cell(0, 8, f'CUIT: {factura["cliente"].get("cuit", "N/D")}', 0, 1)
        pdf.cell(0, 8, f'Condición IVA: {factura["cliente"]["condicionIVA"]}', 0, 1)
        
        pdf.ln(10)
        
        # Items
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(100, 10, 'Descripción', 1)
        pdf.cell(30, 10, 'Cantidad', 1)
        pdf.cell(30, 10, 'Precio', 1)
        pdf.cell(30, 10, 'Subtotal', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for item in factura['items']:
            pdf.cell(100, 8, item['descripcion'][:40], 1)
            pdf.cell(30, 8, str(item['cantidad']), 1)
            pdf.cell(30, 8, f"${item['precioUnitario']:.2f}", 1)
            pdf.cell(30, 8, f"${item['cantidad'] * item['precioUnitario']:.2f}", 1)
            pdf.ln()
        
        # Totales
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Subtotal: ${factura["subtotal"]:.2f}', 0, 1)
        pdf.cell(0, 10, f'IVA (21%): ${factura["iva"]:.2f}', 0, 1)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, f'TOTAL: ${factura["total"]:.2f}', 0, 1)
        
        # CAE
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'CAE: {factura["cae"]}', 0, 1)
        pdf.cell(0, 8, f'Fecha Vto. CAE: {datetime.fromisoformat(factura["fechaVencimientoCAE"]).strftime("%d/%m/%Y")}', 0, 1)
        pdf.cell(0, 8, f'Estado: {factura["estado"]}', 0, 1)
        
        # Guardar en buffer
        pdf_output = pdf.output(dest='S').encode('latin1')
        
        return pdf_output, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=factura_{factura["numero"]}.pdf'
        }
        
    except Exception as e:
        return jsonify({'error': f'Error al generar PDF: {str(e)}'}), 500