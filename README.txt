SIMULADOR DE CONCENTRACIÓN DE MERCADO
======================================

DESCRIPCIÓN
-----------

Aplicación web desarrollada en Python con Streamlit para simular,
visualizar e interpretar la concentración de un mercado mediante
el método de Monte Carlo.

FUNCIONES PRINCIPALES
---------------------

- Número de empresas entre 2 y 100.
- Selección entre CRk, IHH, Índice de Dominancia e Índice de Entropía.
- 1.000 iteraciones por defecto.
- Número de iteraciones modificable.
- Advertencia por carga computacional.
- Generación de cuotas aleatorias mediante distribución Dirichlet.
- Verificación de que las cuotas suman 1.
- Ingreso manual de cuotas.
- Generación aleatoria de un caso particular.
- Histograma de la distribución Monte Carlo.
- Línea vertical del caso particular.
- Cálculo de percentil.
- Pregunta evaluadora.
- Corrección automática.
- Retroalimentación técnica.

ARCHIVOS
--------

app.py
requirements.txt
README.txt

INSTALACIÓN
-----------

1. Instalar Python 3.10 o superior.

2. Abrir una terminal en esta carpeta.

3. Instalar las dependencias:

pip install -r requirements.txt

4. Ejecutar la aplicación:

streamlit run app.py

5. Abrir en el navegador la dirección que muestre Streamlit,
normalmente:

http://localhost:8501

DESPLIEGUE
----------

El proyecto puede publicarse en Streamlit Community Cloud.

Para ello se recomienda subir estos archivos a un repositorio de GitHub:

- app.py
- requirements.txt
- README.txt

Luego conectar el repositorio a Streamlit Community Cloud.
