import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Formulario
signal_type = st.selectbox("Tipo de señal", ["Sinusoidal", "Diente de sierra", "Cuadrada", "Ruido"])
fs = st.slider("Tasa de muestreo (Hz)", 10, 200, 50)
levels = st.selectbox("Cuantización (niveles)", [4, 8, 16, 32])

if st.button("Simular"):
    t = np.linspace(0, 1, 1000)
    if signal_type == "Sinusoidal":
        analog = np.sin(2*np.pi*5*t)
    elif signal_type == "Diente de sierra":
        analog = 2*(t*5 - np.floor(t*5 + 0.5))
    elif signal_type == "Cuadrada":
        analog = np.sign(np.sin(2*np.pi*5*t))
    else:
        analog = np.random.randn(len(t))

    ts = np.arange(0, 1, 1/fs)
    sampled = np.interp(ts, t, analog)
    quantized = np.round(sampled * (levels/2)) / (levels/2)

    fig, ax = plt.subplots()
    ax.plot(t, analog, label="Analógica")
    ax.stem(ts, sampled, linefmt='r-', markerfmt='ro', basefmt=" ", label="Muestreo")
    ax.stem(ts, quantized, linefmt='g-', markerfmt='go', basefmt=" ", label="Cuantización")
    ax.legend()
    st.pyplot(fig)
