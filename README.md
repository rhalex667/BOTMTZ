Markdown

# BOTMTZ
**Versión 1.0 Beta** — *Sujeto a cambios y mejoras*

---
## 📄 Descripción

BOTMTZ es una herramienta desarrollada en **Python** para la resolución de matrices. Está diseñada para procesar dos tipos de entrada de datos:

-   **OCR** (Reconocimiento Óptico de Caracteres) para imágenes de matrices.
-   **Texto estructurado** (formato manual o archivo de texto).

El repositorio incluye:

-   Un archivo `README.md` con instrucciones detalladas.
-   Un archivo `prompt.md` con ejemplos de *prompts* para usar con IA externas.
-   Un módulo para generar un archivo **JSON** con los datos procesados, listo para ser utilizado como *input* en modelos de IA.

---
## ⚠️ Información Importante

-   **Estado actual**: Versión Beta. Puede contener errores.
-   **Pruebas realizadas**: No se han reportado errores de compilación, pero la precisión depende de:
    -   La **claridad de la imagen** (para OCR).
    -   La **estructura y detalle del texto** (para entrada manual).
-   **Estructuras validadas**: Se incluyen ejemplos de estructuras probadas sin margen de error en la sección [Ejemplos de Estructura](#ejemplos-de-estructura).

---
## 📋 Instrucciones de Uso

### 1. **Requisitos Previos**

Para usar BOTMTZ, necesitas las dependencias de Python y el motor OCR externo.

#### A. Dependencias de Python (`req.txt`)

Asegúrate de tener **Python 3.8 o superior** instalado. Luego, instala las dependencias usando el archivo `req.txt`:

```bash
pip install -r req.txt

B. Requisito Externo (Motor Tesseract OCR) 🚨

Para que el procesamiento de imágenes (OCR) funcione, debes instalar el motor Tesseract OCR en tu sistema operativo, ya que no es una librería de Python.
Sistema Operativo	Instrucción de Instalación Sugerida
Linux (Debian/Ubuntu)	sudo apt install tesseract-ocr
macOS (Homebrew)	brew install tesseract
Windows	Descargar el instalador oficial y añadir la ruta de instalación al PATH del sistema.

2. Ejecución

    Abre una terminal en el directorio del repositorio.

    Ejecuta el siguiente comando para iniciar el servicio:
    Bash

    python app.py

    Abre el enlace generado en tu navegador (ejemplo: http://localhost:5000).

3. Procesamiento de Datos

    Subir datos:

        Para OCR: Sube una imagen clara de la matriz.

        Para texto: Pega el texto estructurado en el campo correspondiente.

    Generar JSON:

        El sistema procesará los datos y generará un JSON en pantalla (o un archivo output.json si lo has configurado) con la matriz y metadatos.

    Copiar resultados:

        Copia el contenido del JSON y el archivo prompt.md para usarlos como input en la IA externa de tu preferencia.

4. Obtener Respuesta

    Pega el JSON y el prompt en la IA externa.

    La IA procesará la matriz y devolverá la solución.

📂 Estructura del Repositorio

BOTMTZ/
├── app.py               # Script principal
├── req.txt              # Dependencias de Python
├── prompt.md            # Ejemplos de prompts para IA
├── examples/            # Ejemplos de estructuras validadas
│   ├── matrix_ocr.jpg   # Ejemplo de imagen para OCR
│   └── matrix_text.txt  # Ejemplo de texto estructurado
└── README.md            # Este archivo

📸 Ejemplos de Estructura

1. Entrada por OCR

    Imagen válida: Debe ser clara, con la matriz bien definida y sin distorsiones.

    Ejemplo:

2. Entrada por Texto

A. Sistema de Ecuaciones Lineales (Requiere =) 🎯

Este formato se usa para definir un sistema de ecuaciones y resultará en la Matriz de Coeficientes (A) y el Vector Independiente (b).
Regla	Formato Válido	Ejemplo de Entrada
Separación	Cada ecuación debe ir en una línea separada (usando Enter).	2x + y = 7 x - 3y = 0
Coeficiente 1	Los coeficientes implícitos (1 o -1) pueden omitirse.	x + 2y - z = 5 (Se entiende 1x)
Espacios	Los espacios alrededor de los signos son opcionales.	2x-y+3z=9 o 2x - y + 3z = 9
Variables	Usa letras (ej., x, y, z, a, b). El parser las unifica a mayúsculas.	x + y + z = 1

Ejemplo de entrada (copiable):

a + b = 10
2a - 3b = 5

B. Matriz Simple (No requiere =) 🧮

Este formato se usa para definir una matriz de números o símbolos. Cualquier línea sin el signo = será procesada como una fila de matriz simple.
Regla	Formato Válido	Ejemplo de Entrada
Separación de Filas	Cada fila de la matriz debe ir en una línea separada (usando Enter).	1 2 3 4 5 6
Separación de Columnas	Usa espacios o comas para separar los elementos dentro de una fila.	1, 2, 3 o 1.0 2.5 3
Notación de Borde	Puedes incluir corchetes, paréntesis o barras verticales.	[1 2]\n[3 4] o `
Elementos	Se aceptan números enteros, decimales o símbolos/texto.	10 -2.5 X Y

Ejemplo de entrada (copiable):

[1 -2 0]
[3 4 1]

🔧 Limitaciones y Mejoras Futuras

Limitaciones actuales:

    Depende de la calidad de la imagen para OCR.

    Solo soporta matrices cuadradas en esta versión.

Mejoras planeadas:

    Soporte para matrices rectangulares.

    Integración con APIs de IA para procesamiento automático.

🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras un error o tienes una sugerencia, abre un issue o envía un pull request.

📜 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.
