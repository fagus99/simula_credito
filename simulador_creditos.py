import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página de Streamlit
st.set_page_config(page_title="Simulador de Créditos", layout="wide")
st.title("💰 Simulador y Comparador de Créditos")

st.markdown("""
Esta aplicación te permite simular diferentes opciones de crédito y analizar la tasa real de un préstamo,
considerando el capital que realmente recibes versus el total que devuelves.
""")

# --- Sección 1: Calculadora de Cuotas (Préstamo Estándar) ---
st.header("1. Calculadora de Cuotas (Préstamo Estándar)")
st.markdown("Ingresa los detalles de una oferta de crédito para calcular la cuota mensual y el total a devolver.")

# Columnas para organizar los inputs de la primera sección
col1_1, col1_2 = st.columns(2)

with col1_1:
    # Input para el importe del préstamo (capital)
    importe_prestamo = st.number_input(
        "Importe a sacar de préstamo (Capital)",
        min_value=0.0,
        value=1000000.0, # Valor inicial de ejemplo
        step=10000.0,
        format="%.2f"
    )
    # Input para la cantidad de cuotas
    cantidad_cuotas = st.number_input(
        "Cantidad de cuotas",
        min_value=1,
        value=24, # Valor inicial de ejemplo
        step=1
    )
    # Input para la Tasa Nominal Anual (TNA)
    tna = st.number_input(
        "Tasa Nominal Anual (TNA) en %",
        min_value=0.0,
        value=9.0, # Valor inicial de ejemplo
        step=0.1,
        format="%.2f"
    )

with col1_2:
    st.markdown("---") # Separador visual para los datos adicionales
    st.write("Datos Adicionales de la Oferta (solo para referencia, no usados en cálculo de cuota):")
    # Inputs para CFTNA y CFTEA (estos valores suelen ser informados por el banco, no calculados aquí sin conocer todos los costos)
    cftna = st.number_input(
        "Costo Financiero Total Nominal Anual (CFTNA) en %",
        min_value=0.0,
        value=0.0, # Valor inicial de ejemplo
        step=0.1,
        format="%.2f"
    )
    cftea = st.number_input(
        "Costo Financiero Total Efectivo Anual (CFTEA) en %",
        min_value=0.0,
        value=0.0, # Valor inicial de ejemplo
        step=0.1,
        format="%.2f"
    )

# Botón para ejecutar el cálculo de la primera sección
if st.button("Calcular Cuota y Total a Devolver"):
    if importe_prestamo > 0 and cantidad_cuotas > 0:
        tna_mensual = (tna / 100) / 12 # Convertir TNA a tasa mensual

        # Cálculo de la cuota mensual usando la fórmula del Sistema Francés
        if tna_mensual > 0:
            cuota_mensual = importe_prestamo * (tna_mensual * (1 + tna_mensual)**cantidad_cuotas) / ((1 + tna_mensual)**cantidad_cuotas - 1)
        else: # Caso especial para TNA 0%
            cuota_mensual = importe_prestamo / cantidad_cuotas

        total_a_devolver = cuota_mensual * cantidad_cuotas

        st.subheader("Resultados del Préstamo Estándar:")
        # Mostrar los resultados formateados como moneda
        st.metric("Cuota Mensual Estimada", f"${cuota_mensual:,.2f}")
        st.metric("Monto Total a Devolver", f"${total_a_devolver:,.2f}")
        st.info(
            f"**Nota:** La TNA es la tasa de interés pura. El CFTNA ({cftna:,.2f}%) y CFTEA ({cftea:,.2f}%) "
            "incluyen otros costos (seguros, comisiones, impuestos) y representan el costo real total del crédito. "
            "Estos últimos no se calculan aquí directamente sin conocer sus componentes."
        )
    else:
        st.warning("Por favor, ingresa un importe de préstamo y cantidad de cuotas válidos.")

st.markdown("---") # Separador entre secciones

# --- Sección 2: Análisis de Préstamo (Cálculo de Tasa Real) ---
st.header("2. Análisis de Préstamo (Cálculo de Tasa Real)")
st.markdown("Ingresa el capital que realmente recibes y el total que devolverás para calcular la tasa de interés efectiva real.")

# Columnas para organizar los inputs de la segunda sección
col2_1, col2_2 = st.columns(2)

with col2_1:
    # Input para el capital inicial realmente recibido (después de gastos)
    capital_inicial_recibido = st.number_input(
        "Capital inicial realmente recibido",
        min_value=0.0,
        value=10300000.0, # Valor inicial de ejemplo (tu caso de 12M - 1.7M)
        step=10000.0,
        format="%.2f",
        key="capital_recibido" # Clave única para este widget
    )
    # Input para el importe total que se va a devolver
    importe_a_devolver_analisis = st.number_input(
        "Importe total a devolver",
        min_value=0.0,
        value=12000000.0, # Valor inicial de ejemplo
        step=10000.0,
        format="%.2f",
        key="total_devolver" # Clave única para este widget
    )
    # Input para la cantidad de cuotas en este análisis
    cantidad_cuotas_analisis = st.number_input(
        "Cantidad de cuotas",
        min_value=1,
        value=18, # Valor inicial de ejemplo
        step=1,
        key="cuotas_analisis" # Clave única para este widget
    )

# Botón para ejecutar el cálculo de la tasa real
if st.button("Calcular Tasa Real del Préstamo"):
    if capital_inicial_recibido > 0 and importe_a_devolver_analisis > 0 and cantidad_cuotas_analisis > 0:
        if importe_a_devolver_analisis < capital_inicial_recibido:
            st.error("El importe total a devolver no puede ser menor que el capital inicial recibido.")
        else:
            # Calcular la cuota mensual implícita
            cuota_mensual_analisis = importe_a_devolver_analisis / cantidad_cuotas_analisis
            
            try:
                # Usamos np.rate para encontrar la tasa mensual implícita
                # nper: número de períodos (cuotas)
                # pmt: pago por período (cuota mensual, negativo porque es una salida de efectivo)
                # pv: valor presente (capital realmente recibido, positivo porque es una entrada de efectivo)
                # fv: valor futuro (0, al final del préstamo)
                # type: 0 para pagos al final del período (lo más común)
                tasa_mensual_real = np.rate(
                    cantidad_cuotas_analisis,
                    -cuota_mensual_analisis, # El pago es una salida, por eso es negativo
                    capital_inicial_recibido, # El capital recibido es una entrada
                    0, # Valor futuro es 0 (el préstamo se salda)
                    0 # Pagos al final del período
                )
                
                # Calcular la Tasa Efectiva Anual (TEA) a partir de la tasa mensual real
                tasa_anual_efectiva_real = (1 + tasa_mensual_real)**12 - 1
                
                st.subheader("Resultados del Análisis de Tasa Real:")
                # Mostrar los resultados formateados como porcentaje
                st.metric("Tasa Mensual Efectiva Real", f"{tasa_mensual_real * 100:,.2f}%")
                st.metric("Tasa Efectiva Anual Real (TEA)", f"{tasa_anual_efectiva_real * 100:,.2f}%")
                st.success("Esta TEA refleja el costo real del dinero que recibes, considerando todos los gastos iniciales y el monto total a devolver.")
            except Exception as e:
                st.error(f"No se pudo calcular la tasa real. Asegúrate de que los valores sean consistentes. Error: {e}")
    else:
        st.warning("Por favor, ingresa valores válidos para el capital recibido, el total a devolver y la cantidad de cuotas.")

st.markdown("---")
st.markdown("Desarrollado para comparar y entender mejor los costos de los créditos.")