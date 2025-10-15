import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import json
import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

# --- CONFIGURACIÓN DE FLASK Y ARCHIVOS ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- CONFIGURACIÓN DE TESSERACT (AJUSTA ESTO SI ES NECESARIO) ---
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====================================================================
# === FUNCIONES DE PROCESAMIENTO CENTRAL (CORREGIDAS) ===
# ====================================================================

# 1. Preprocesamiento de Imagen (Usando OpenCV)
def preprocesar_pizarra(ruta_imagen):
    """Mejora la imagen para OCR."""
    img = cv2.imread(ruta_imagen)
    if img is None: raise FileNotFoundError(f"No se pudo cargar la imagen: {ruta_imagen}")
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    invertida = cv2.bitwise_not(gris) 
    umbral = cv2.adaptiveThreshold(invertida, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 4) 
    factor_escala = 3
    mejorada = cv2.resize(umbral, None, fx=factor_escala, fy=factor_escala, interpolation=cv2.INTER_CUBIC)
    return Image.fromarray(mejorada)

# 2. Funciones para Sistema de Ecuaciones
def extraer_ecuaciones(texto_crudo):
    # Ya se asume que el texto crudo ha sido normalizado con saltos de línea reales.
    ecuaciones_validas = re.findall(r'.*[a-zA-Z].*=.+', texto_crudo)
    return [re.sub(r'\s+', ' ', eq.strip()) for eq in ecuaciones_validas]

def detectar_variables(ecuaciones):
    vars_encontradas = set()
    for eq in ecuaciones:
        for var in re.findall(r'[a-zA-Z]', eq):
            vars_encontradas.add(var.upper())
    return sorted(list(vars_encontradas))

def extraer_coeficientes_y_resultado(ecuacion, variables):
    eq_original = ecuacion.replace('−', '-').replace('–', '-')
    
    # Aseguramos que la ecuación NO contenga saltos de línea escapados o reales.
    if '\n' in eq_original:
        # Esto debería haber sido manejado por procesar_texto_a_json, 
        # pero es una capa de seguridad para evitar errores de 'unpack'
        eq_original = eq_original.replace('\n', ' ').strip() 
        
    if '=' not in eq_original:
        raise ValueError("La línea no contiene el signo de igualdad (=).")

    eq_lower = eq_original.lower()
    
    # Si la ecuación es solo 'X = Y', split puede fallar, comprobamos que haya dos partes
    partes = eq_lower.split('=', 1)
    if len(partes) != 2:
        raise ValueError("La ecuación no está bien formada para split (falta lado derecho o izquierdo).")
        
    izquierda, derecha = partes
    derecha_strip = eq_original.split('=', 1)[1].strip()

    coefs = []
    for var in variables:
        var_lower = var.lower()
        patron = rf'([+\-]?\s*\d*\.?\d*)\s*{re.escape(var_lower)}' 
        match = re.search(patron, izquierda)
        
        if match:
            signo_y_valor = match.group(1).replace(' ', '')
            
            if signo_y_valor in ['', '+']: coefs.append(1.0)
            elif signo_y_valor == '-': coefs.append(-1.0)
            else: coefs.append(float(signo_y_valor))
        else:
            coefs.append(0.0)
    
    try:
        b = float(derecha_strip)
    except ValueError:
        b = derecha_strip
    return coefs, b

def generar_json_sistema(texto_crudo, fuente, ruta_origen=""):
    """Genera el JSON estructurado del sistema de ecuaciones."""
    try:
        ecuaciones = extraer_ecuaciones(texto_crudo)
        if not ecuaciones:
            raise ValueError("No se detectaron ecuaciones válidas. Texto crudo no es un sistema.")
            
        variables = detectar_variables(ecuaciones)
        
        matriz_coef = []
        vector_b = []
        for eq in ecuaciones:
            # Aquí la función extraer_coeficientes_y_resultado espera una sola ecuación
            coefs, b = extraer_coeficientes_y_resultado(eq, variables)
            matriz_coef.append(coefs)
            vector_b.append(b)
        
        matriz_aumentada = [fila + [b] for fila, b in zip(matriz_coef, vector_b)]
        
        instrucciones = (
            "Esta estructura fue clasificada como 'Sistema Lineal' porque se detectó el signo '=' en el texto. "
            "Las variables han sido unificadas a mayúsculas. Se debe validar el campo 'vector_independiente' por si contiene símbolos."
        )

        return {
            "nombre": "Sistema_Ecuaciones_OCR",
            "tipo_estructura": "Sistema Lineal",
            "notacion_borde": "No aplica (texto de ecuaciones)",
            "dimensiones": {"ecuaciones": len(ecuaciones), "incognitas": len(variables)},
            "variables": variables,
            "matriz_coeficientes": matriz_coef,
            "vector_independiente": vector_b,
            "matriz_aumentada": matriz_aumentada,
            "representacion_simbolica": ecuaciones,
            "metadatos": {
                "fuente": fuente,
                "ruta_origen": ruta_origen,
                "texto_ocr_crudo": texto_crudo.strip(),
                "instrucciones_ia": instrucciones
            },
            "validacion": {"estado": "válido", "por": "OCR-MATH-v8"}
        }
    except Exception as e:
        # Se asegura de que si hay un error, el texto crudo sea legible
        return {"error": f"Error en el procesamiento del sistema de ecuaciones: {str(e)}", "texto_crudo": texto_crudo}


# 3. Función para Matriz Simple
def parsear_matriz_simple(texto_crudo, nombre_matriz="Matriz_Simple", fuente="", ruta_origen=""):
    """Procesa texto crudo sin signos de igual, asumiendo una matriz de números/variables."""
    # Como el texto_crudo ya está normalizado (saltos de línea reales), lo dividimos por líneas
    lineas = [l.strip() for l in texto_crudo.split('\n') if l.strip()]
    datos_matriz = []
    notacion_detectada = "No detectada"
    patron_notacion = re.compile(r'^\s*([(\[{\|])(.*)([)\]\}\|])\s*$')
    
    for linea in lineas:
        match = patron_notacion.match(linea)
        
        if match:
            linea_a_parsear = match.group(2).strip()
            if notacion_detectada == "No detectada":
                inicio, fin = match.group(1), match.group(3)
                if inicio == '|' and fin == '|': notacion_detectada = "Barras Verticales (| |)"
                elif inicio == '(' and fin == ')': notacion_detectada = "Paréntesis ( )"
                elif inicio == '[' and fin == ']': notacion_detectada = "Corchetes [ ]"
                else: notacion_detectada = f"{inicio} {fin}"
        else:
            linea_a_parsear = linea
        
        elementos = re.split(r'\s+|,', linea_a_parsear)
        
        fila = []
        for elemento in elementos:
            if not elemento: continue
            try:
                if '.' in elemento or 'e' in elemento.lower(): fila.append(float(elemento))
                else: fila.append(int(elemento))
            except ValueError: fila.append(elemento)
        if fila: datos_matriz.append(fila)

    if not datos_matriz:
        raise ValueError("No se detectaron filas de matriz válidas.")

    longitud_primera_fila = len(datos_matriz[0]) if datos_matriz else 0
    
    instrucciones = (
        "Esta estructura fue clasificada como 'Matriz Simple' porque NO se detectó el signo '=' en el texto. "
        "Contiene solo filas de datos (coeficientes/valores). El campo 'filas' es la matriz A o B. "
        "Se recomienda validar el tipo de datos en 'filas' (números o símbolos)."
    )

    return {
        "nombre": nombre_matriz,
        "tipo_estructura": "Matriz Simple",
        "notacion_borde": notacion_detectada,
        "dimensiones": f"{len(datos_matriz)}x{longitud_primera_fila}",
        "filas": datos_matriz,
        "metadatos": {
            "fuente": fuente,
            "ruta_origen": ruta_origen,
            "texto_ocr_crudo": texto_crudo.strip(),
            "instrucciones_ia": instrucciones
        },
        "validacion": {"estado": "válido", "por": "OCR-MATH-v7"}
    }


# 4. Función de Decisión General (PUNTO CLAVE DE CORRECCIÓN)
def procesar_texto_a_json(texto_crudo, fuente, ruta_origen=""):
    """
    Decide si procesar como Sistema de Ecuaciones o Matriz Simple.
    
    NOTA IMPORTANTE: Se normaliza la cadena reemplazando '\\n' con '\n' 
    para asegurar que los saltos de línea sean interpretados correctamente, 
    especialmente para la entrada de texto directo del frontend.
    """
    # 💥 CORRECCIÓN CRÍTICA DE SALTO DE LÍNEA 💥
    texto_normalizado = texto_crudo.replace('\\n', '\n').strip()

    if "=" in texto_normalizado:
        return generar_json_sistema(texto_normalizado, fuente, ruta_origen)
    else:
        return parsear_matriz_simple(texto_normalizado, "Matriz_OCR_Manual" if fuente == "TEXTO_DIRECTO" else "Matriz_OCR_Imagen", fuente, ruta_origen)


# ====================================================================
# === RUTAS DE FLASK ===
# ====================================================================

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/procesar_texto', methods=['POST'])
def procesar_texto():
    data = request.get_json()
    # Asume que el texto del frontend ya tiene los saltos de línea codificados como '\n'
    texto = data.get('texto', '').strip()
    
    if not texto:
        return jsonify({"error": "El campo de texto no puede estar vacío."}), 400
        
    try:
        # La corrección del salto de línea se realiza dentro de procesar_texto_a_json
        resultado_json = procesar_texto_a_json(texto, fuente="TEXTO_DIRECTO")
        
        if "error" in resultado_json:
            return jsonify(resultado_json), 500
            
        return jsonify(resultado_json)
        
    except Exception as e:
        error_msg = f"Error interno en el procesamiento de texto. Detalle: {str(e)}"
        return jsonify({"error": error_msg}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    # ... (Lógica de subida y OCR, se omiten aquí para concisión)
    # ... El texto del OCR ya viene con '\n' real, por lo que la normalización es segura
    pass 

if __name__ == '__main__':
    # No olvides volver a incluir la lógica completa de upload_file si la omitiste.
    # Aquí solo se muestra la parte relevante.
    app.run(debug=True)