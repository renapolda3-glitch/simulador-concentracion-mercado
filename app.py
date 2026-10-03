import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Simulador de Concentración de Mercado",
    page_icon="📊",
    layout="wide"
)

st.title("Simulador de Concentración de Mercado")
st.write(
    """
    Esta aplicación permite simular, visualizar e interpretar la concentración
    de un mercado mediante el método de Monte Carlo. El usuario puede seleccionar
    un indicador, definir el número de empresas, generar mercados aleatorios,
    ingresar un caso particular y compararlo con una distribución simulada.
    """
)

st.info(
    """
    En cada iteración, las cuotas de mercado cumplen la condición de cierre:

    Σ si = 1

    Es decir, la suma de las participaciones de todas las empresas equivale al 100%.
    """
)

# =========================================================
# FUNCIONES DE INDICADORES
# =========================================================

def calcular_crk(cuotas, k):
    cuotas_ordenadas = np.sort(cuotas)[::-1]
    return np.sum(cuotas_ordenadas[:k]) * 100


def calcular_ihh(cuotas):
    return np.sum(cuotas ** 2) * 10000


def calcular_dominancia(cuotas):
    ihh_decimal = np.sum(cuotas ** 2)
    if ihh_decimal == 0:
        return 0.0
    return np.sum(cuotas ** 4) / (ihh_decimal ** 2)


def calcular_entropia(cuotas):
    cuotas_positivas = cuotas[cuotas > 0]
    entropia = -np.sum(cuotas_positivas * np.log(cuotas_positivas))
    entropia_maxima = np.log(len(cuotas))

    if entropia_maxima == 0:
        return 0.0

    return entropia / entropia_maxima


def calcular_indicador(cuotas, indicador, k=4):
    if indicador == "Ratio de Concentración (CRk)":
        return calcular_crk(cuotas, k)
    elif indicador == "Índice Herfindahl-Hirschman (IHH)":
        return calcular_ihh(cuotas)
    elif indicador == "Índice de Dominancia (ID)":
        return calcular_dominancia(cuotas)
    elif indicador == "Índice de Entropía (IE)":
        return calcular_entropia(cuotas)


# =========================================================
# FUNCIÓN VECTORIAL PARA MONTE CARLO
# =========================================================

def calcular_monte_carlo(simulaciones, indicador, k):
    if indicador == "Ratio de Concentración (CRk)":
        ordenadas = np.sort(simulaciones, axis=1)[:, ::-1]
        return np.sum(ordenadas[:, :k], axis=1) * 100

    elif indicador == "Índice Herfindahl-Hirschman (IHH)":
        return np.sum(simulaciones ** 2, axis=1) * 10000

    elif indicador == "Índice de Dominancia (ID)":
        ihh_decimal = np.sum(simulaciones ** 2, axis=1)
        numerador = np.sum(simulaciones ** 4, axis=1)
        return numerador / (ihh_decimal ** 2)

    elif indicador == "Índice de Entropía (IE)":
        seguros = np.clip(simulaciones, 1e-15, 1)
        entropia = -np.sum(seguros * np.log(seguros), axis=1)
        return entropia / np.log(simulaciones.shape[1])


# =========================================================
# CONFIGURACIÓN DEL MERCADO
# =========================================================

st.header("1. Configuración del mercado")

col1, col2 = st.columns(2)

with col1:
    numero_empresas = st.number_input(
        "Número de empresas (N)",
        min_value=2,
        max_value=100,
        value=5,
        step=1
    )

with col2:
    indicador = st.selectbox(
        "Seleccione un indicador de concentración",
        [
            "Ratio de Concentración (CRk)",
            "Índice Herfindahl-Hirschman (IHH)",
            "Índice de Dominancia (ID)",
            "Índice de Entropía (IE)"
        ]
    )

numero_empresas = int(numero_empresas)

k = min(4, numero_empresas)

if indicador == "Ratio de Concentración (CRk)":
    k = int(
        st.number_input(
            "Seleccione el valor de k",
            min_value=1,
            max_value=numero_empresas,
            value=min(4, numero_empresas),
            step=1
        )
    )

# =========================================================
# CONFIGURACIÓN DE ITERACIONES
# =========================================================

st.header("2. Simulación de Monte Carlo")

iteraciones = int(
    st.number_input(
        "Número de iteraciones",
        min_value=100,
        max_value=50000,
        value=1000,
        step=100
    )
)

if iteraciones <= 5000:
    st.success("Carga computacional baja o moderada.")
elif iteraciones <= 20000:
    st.warning(
        "Al aumentar las iteraciones también aumenta el tiempo de procesamiento "
        "y la latencia de respuesta."
    )
else:
    st.error(
        "Advertencia: una cantidad superior a 20.000 iteraciones puede aumentar "
        "considerablemente el consumo de memoria, recursos de cómputo y tiempo de respuesta."
    )

st.write(
    """
    Para generar los vectores de cuotas se utiliza una distribución Dirichlet.
    Esta distribución permite obtener participaciones no negativas cuya suma
    es igual a 1 en cada iteración.
    """
)

if st.button("Ejecutar simulación Monte Carlo", type="primary"):

    simulaciones = np.random.dirichlet(
        np.ones(numero_empresas),
        size=iteraciones
    )

    # Refuerzo numérico de la condición de cierre
    simulaciones = simulaciones / simulaciones.sum(axis=1, keepdims=True)

    resultados = calcular_monte_carlo(
        simulaciones,
        indicador,
        k
    )

    st.session_state["simulaciones"] = simulaciones
    st.session_state["resultados"] = resultados
    st.session_state["configuracion"] = (
        numero_empresas,
        indicador,
        k,
        iteraciones
    )

    st.success(f"Se ejecutaron correctamente {iteraciones:,} simulaciones.")

# =========================================================
# VERIFICACIÓN DE CIERRE
# =========================================================

if "simulaciones" in st.session_state:

    simulaciones = st.session_state["simulaciones"]
    sumas = simulaciones.sum(axis=1)

    st.subheader("Verificación matemática")

    c1, c2, c3 = st.columns(3)

    c1.metric("Suma mínima", f"{sumas.min():.12f}")
    c2.metric("Suma máxima", f"{sumas.max():.12f}")
    c3.metric(
        "Error máximo",
        f"{np.max(np.abs(sumas - 1)):.2e}"
    )

    if np.allclose(sumas, 1.0):
        st.success(
            "Todas las simulaciones cumplen la condición Σ si = 1 "
            "dentro de la precisión numérica."
        )

# =========================================================
# CASO PARTICULAR
# =========================================================

st.header("3. Caso particular")

modo = st.radio(
    "Seleccione cómo desea definir el caso particular",
    [
        "Generación aleatoria",
        "Entrada manual"
    ],
    horizontal=True
)

if modo == "Generación aleatoria":

    if st.button("Generar caso aleatorio"):

        cuotas_caso = np.random.dirichlet(
            np.ones(numero_empresas)
        )

        st.session_state["cuotas_caso"] = cuotas_caso

else:

    st.write(
        f"Ingrese exactamente {numero_empresas} cuotas en porcentaje, separadas por comas."
    )

    st.caption(
        "Ejemplo para 4 empresas: 40, 30, 20, 10"
    )

    texto = st.text_input(
        "Cuotas de mercado (%)"
    )

    if st.button("Guardar caso manual"):

        try:

            cuotas_manual = np.array(
                [
                    float(x.strip())
                    for x in texto.split(",")
                ]
            )

            if len(cuotas_manual) != numero_empresas:
                st.error(
                    f"Debe ingresar exactamente {numero_empresas} valores."
                )

            elif np.any(cuotas_manual < 0):
                st.error(
                    "Las cuotas no pueden ser negativas."
                )

            elif np.any(cuotas_manual > 100):
                st.error(
                    "Ninguna cuota puede superar el 100%."
                )

            elif not np.isclose(
                cuotas_manual.sum(),
                100,
                atol=0.01
            ):
                st.error(
                    f"Las cuotas deben sumar 100%. "
                    f"Actualmente suman {cuotas_manual.sum():.2f}%."
                )

            else:

                st.session_state["cuotas_caso"] = (
                    cuotas_manual / 100
                )

                st.success(
                    "Caso particular guardado correctamente."
                )

        except ValueError:

            st.error(
                "Ingrese solamente números separados por comas."
            )

# =========================================================
# MOSTRAR CASO
# =========================================================

valor_caso = None

if "cuotas_caso" in st.session_state:

    cuotas_caso = st.session_state["cuotas_caso"]

    if len(cuotas_caso) == numero_empresas:

        tabla = pd.DataFrame(
            {
                "Empresa": [
                    f"Empresa {i + 1}"
                    for i in range(numero_empresas)
                ],
                "Cuota de mercado (%)": np.round(
                    cuotas_caso * 100,
                    2
                )
            }
        )

        st.subheader("Cuotas del caso particular")

        st.dataframe(
            tabla,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"**Suma total: {cuotas_caso.sum() * 100:.2f}%**"
        )

        valor_caso = calcular_indicador(
            cuotas_caso,
            indicador,
            k
        )

        if indicador == "Ratio de Concentración (CRk)":

            st.metric(
                f"Resultado CR{k}",
                f"{valor_caso:.2f}%"
            )

        elif indicador == "Índice Herfindahl-Hirschman (IHH)":

            st.metric(
                "Resultado IHH",
                f"{valor_caso:.2f}"
            )

        else:

            st.metric(
                "Resultado",
                f"{valor_caso:.4f}"
            )

    else:
        st.warning(
            "El número de empresas cambió. Genere nuevamente el caso particular."
        )

# =========================================================
# GRÁFICO COMPARATIVO
# =========================================================

percentil = None

if (
    "resultados" in st.session_state
    and valor_caso is not None
):

    resultados = st.session_state["resultados"]

    percentil = (
        np.mean(resultados <= valor_caso)
        * 100
    )

    st.header("4. Comparación con la distribución Monte Carlo")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        resultados,
        bins=30,
        alpha=0.75,
        edgecolor="black"
    )

    ax.axvline(
        valor_caso,
        linewidth=3,
        linestyle="--",
        label="Caso particular"
    )

    ax.set_title(
        "Distribución empírica del indicador"
    )

    ax.set_xlabel(
        "Valor del indicador"
    )

    ax.set_ylabel(
        "Frecuencia"
    )

    ax.legend()

    st.pyplot(fig)

    st.write(
        f"""
        El caso particular se ubica aproximadamente en el
        **percentil {percentil:.2f}** de los escenarios simulados.
        """
    )

# =========================================================
# MÓDULO EVALUADOR
# =========================================================

if valor_caso is not None:

    st.header("5. Pregunta evaluadora y retroalimentación")

    st.write(
        """
        **Pregunta:** Según el valor obtenido en el caso particular,
        ¿cómo clasificaría el nivel de concentración del mercado?
        """
    )

    respuesta = st.radio(
        "Seleccione una respuesta",
        [
            "Baja concentración",
            "Concentración moderada",
            "Alta concentración"
        ],
        index=None
    )

    respuesta_correcta = None
    explicacion = ""

    # -----------------------------------------------------
    # IHH
    # -----------------------------------------------------

    if indicador == "Índice Herfindahl-Hirschman (IHH)":

        if valor_caso < 1500:
            respuesta_correcta = "Baja concentración"
        elif valor_caso <= 2500:
            respuesta_correcta = "Concentración moderada"
        else:
            respuesta_correcta = "Alta concentración"

        explicacion = (
            f"El IHH del caso es {valor_caso:.2f}. "
            "Para fines académicos, se usa la clasificación tradicional: "
            "menos de 1.500 puntos corresponde a baja concentración, "
            "entre 1.500 y 2.500 a concentración moderada y "
            "sobre 2.500 a alta concentración."
        )

    # -----------------------------------------------------
    # CR4
    # -----------------------------------------------------

    elif (
        indicador == "Ratio de Concentración (CRk)"
        and k == 4
    ):

        if valor_caso < 40:
            respuesta_correcta = "Baja concentración"
        elif valor_caso <= 60:
            respuesta_correcta = "Concentración moderada"
        else:
            respuesta_correcta = "Alta concentración"

        explicacion = (
            f"El CR4 del caso es {valor_caso:.2f}%. "
            "En esta aplicación se utiliza como criterio pedagógico: "
            "menos de 40% = baja concentración, "
            "entre 40% y 60% = moderada y "
            "sobre 60% = alta concentración."
        )

    # -----------------------------------------------------
    # CRk DISTINTO DE 4
    # -----------------------------------------------------

    elif indicador == "Ratio de Concentración (CRk)":

        if percentil is None:
            respuesta_correcta = "Concentración moderada"
            explicacion = (
                "Ejecute primero la simulación Monte Carlo para comparar "
                "este CRk con la distribución simulada."
            )
        else:
            if percentil < 33.33:
                respuesta_correcta = "Baja concentración"
            elif percentil < 66.67:
                respuesta_correcta = "Concentración moderada"
            else:
                respuesta_correcta = "Alta concentración"

            explicacion = (
                f"Para CR{k}, esta aplicación utiliza una clasificación "
                f"relativa respecto de la simulación Monte Carlo. "
                f"El caso se encuentra en el percentil {percentil:.2f}."
            )

    # -----------------------------------------------------
    # ÍNDICE DE DOMINANCIA
    # -----------------------------------------------------

    elif indicador == "Índice de Dominancia (ID)":

        if valor_caso < 0.25:
            respuesta_correcta = "Baja concentración"
        elif valor_caso <= 0.50:
            respuesta_correcta = "Concentración moderada"
        else:
            respuesta_correcta = "Alta concentración"

        explicacion = (
            f"El Índice de Dominancia es {valor_caso:.4f}. "
            "Valores mayores indican mayor peso relativo de una o pocas empresas. "
            "Los puntos de corte usados aquí son pedagógicos, porque este indicador "
            "no posee una clasificación normativa única y universal."
        )

    # -----------------------------------------------------
    # ÍNDICE DE ENTROPÍA
    # -----------------------------------------------------

    elif indicador == "Índice de Entropía (IE)":

        if valor_caso > 0.75:
            respuesta_correcta = "Baja concentración"
        elif valor_caso >= 0.50:
            respuesta_correcta = "Concentración moderada"
        else:
            respuesta_correcta = "Alta concentración"

        explicacion = (
            f"El Índice de Entropía normalizado es {valor_caso:.4f}. "
            "A diferencia del IHH, valores cercanos a 1 indican cuotas "
            "más uniformemente distribuidas y, por tanto, menor concentración. "
            "Los puntos de corte utilizados son de carácter pedagógico."
        )

    if respuesta is not None:

        if respuesta == respuesta_correcta:

            st.success(
                "Respuesta correcta."
            )

        else:

            st.error(
                f"Respuesta incorrecta. "
                f"La clasificación correspondiente es: "
                f"{respuesta_correcta}."
            )

        st.info(
            explicacion
        )

# =========================================================
# INFORMACIÓN METODOLÓGICA
# =========================================================

st.header("6. Fundamento metodológico")

st.write(
    """
    ### Simulación de Monte Carlo

    El método de Monte Carlo consiste en repetir numerosas veces un experimento
    aleatorio para estudiar la distribución de posibles resultados.

    En esta aplicación, cada iteración genera un mercado compuesto por N empresas.
    Las cuotas se obtienen mediante una distribución Dirichlet, que permite cumplir
    la condición de cierre de las participaciones.

    Posteriormente se calcula el indicador seleccionado en cada mercado simulado,
    obteniéndose una distribución empírica. El caso particular del usuario se
    compara con esta distribución mediante un marcador vertical y su percentil.
    """
)

st.write(
    """
    ### Indicadores utilizados

    **Ratio de Concentración CRk:** suma de las cuotas de las k empresas más grandes.

    **Índice Herfindahl-Hirschman (IHH):** suma de los cuadrados de las cuotas de mercado.

    **Índice de Dominancia (ID):** medida de dominancia basada en la participación
    relativa de las empresas dentro de la estructura del IHH.

    **Índice de Entropía (IE):** mide el grado de uniformidad de las cuotas.
    En esta aplicación se normaliza entre 0 y 1.
    """
)

st.caption(
    "Aplicación académica desarrollada en Python con Streamlit, NumPy, Pandas y Matplotlib."
)
