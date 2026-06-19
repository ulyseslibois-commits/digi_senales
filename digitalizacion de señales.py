import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import io

# Archivo CSV donde guardaremos los datos
csv_file = "simulaciones.csv"

# Formulario
signal_type = st.selectbox("Tipo de señal", ["Sinusoidal", "Diente de sierra", "Cuadrada", "Ruido"])
fs = st.slider("Tasa de muestreo (Hz)", 1, 200, 50)
levels = st.selectbox("Cuantización (niveles)", [4, 8, 16, 32])
normalize = st.checkbox("Normalizar señal antes de cuantizar", value=True)

if st.button("Simular"):
    f_max = 5  # frecuencia máxima de la señal (ejemplo fijo)
    if fs < 2 * f_max:
        st.warning(f"La tasa de muestreo ({fs} Hz) es menor que el doble de la frecuencia máxima ({2*f_max} Hz). Puede producirse aliasing.")

    t = np.linspace(0, 1, 1000)
    if signal_type == "Sinusoidal":
        analog = np.sin(2*np.pi*f_max*t)
    elif signal_type == "Diente de sierra":
        analog = 2*(t*f_max - np.floor(t*f_max + 0.5))
    elif signal_type == "Cuadrada":
        analog = np.sign(np.sin(2*np.pi*f_max*t))
    else:
        analog = np.random.randn(len(t))

    ts = np.arange(0, 1, 1/fs)
    sampled = np.interp(ts, t, analog)

    # Cuantización con o sin normalización
    if normalize:
        sampled_norm = (sampled - sampled.min()) / (sampled.max() - sampled.min())
        quantized = np.round(sampled_norm * (levels-1)) / (levels-1)
    else:
        min_val, max_val = -1.0, 1.0
        quantized = np.round((sampled - min_val) / (max_val - min_val) * (levels-1))
        quantized = quantized / (levels-1) * (max_val - min_val) + min_val

    fig, ax = plt.subplots()
    ax.plot(t, analog, label="Analógica")
    ax.plot(ts, sampled, 'ro', label="Muestreo")
    ax.stem(ts, quantized, linefmt='g-', markerfmt='go', basefmt=" ", label="Cuantización")
    ax.set_title("Digitalización de señales")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud")
    ax.legend()
    st.pyplot(fig)

    # Crear columna "digi" como identificador incremental
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        digi_id = len(df) + 1
    else:
        digi_id = 1

    new_data = pd.DataFrame({
        "digi": [digi_id],
        "Tipo de señal": [signal_type],
        "Tasa de muestreo": [fs],
        "Niveles": [levels],
        "Normalizado": [normalize]
    })

    if os.path.exists(csv_file):
        new_data.to_csv(csv_file, mode="a", header=False, index=False)
    else:
        new_data.to_csv(csv_file, index=False)

    st.success(f"Configuración guardada en CSV con digi={digi_id}")

    # Guardar la figura en memoria como PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Botón de descarga usando el valor de la columna "digi"
    file_name = f"digi_{digi_id}.png"
    st.download_button(
        label="Descargar imagen",
        data=buf,
        file_name=file_name,
        mime="image/png"
    )

# Mostrar historial de simulaciones
if os.path.exists(csv_file):
    st.subheader("Historial de simulaciones")
    df = pd.read_csv(csv_file)
    st.dataframe(df)
