import streamlit as st
import os
import re
import requests
import base64
from googleapiclient.discovery import build

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Estos valores se configuran en el panel de Streamlit Cloud (Secrets)
API_KEY = st.secrets["YOUTUBE_API_KEY"]
GITHUB_TOKEN = st.secrets["GH_TOKEN"]
REPO_NAME = "tareadelau0-blip/Playlist-API"
PASSWORD_APP = st.secrets["APP_PASSWORD"]

st.set_page_config(page_title="Music Manager Pro", page_icon="🎬", layout="wide")

# --- LOGIN SIMPLE ---
st.sidebar.title("🔐 Acceso")
password = st.sidebar.text_input("Contraseña de Administrador", type="password")

if password != PASSWORD_APP:
    st.warning("Por favor, introduce la contraseña en el menú lateral para gestionar las listas.")
    st.stop() # Detiene la app si la clave es incorrecta

# --- FUNCIONES DE GITHUB API ---
def actualizar_listas_en_github(nuevo_enlace):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/listas.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 1. Obtener el archivo actual (necesitamos el 'sha')
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        contenido_actual = base64.b64decode(data['content']).decode('utf-8')
        sha = data['sha']
        nuevo_contenido = contenido_actual + f"\n{nuevo_enlace}"
    else:
        nuevo_contenido = nuevo_enlace
        sha = None

    # 2. Subir el cambio
    payload = {
        "message": "Update listas.txt via Streamlit",
        "content": base64.b64encode(nuevo_contenido.encode('utf-8')).decode('utf-8'),
        "sha": sha if sha else ""
    }
    
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code == 200

# --- INTERFAZ ---
st.title("🎵 Panel de Control - Playlist API")
enlace = st.text_input("Pega el link de la Playlist:")

if st.button("🚀 Agregar al Inventario"):
    if "list=" in enlace:
        if actualizar_listas_en_github(enlace):
            st.success("✅ ¡Enlace guardado en GitHub! Actions lo procesará pronto.")
            st.balloons()
        else:
            st.error("❌ Error al conectar con la API de GitHub.")
    else:
        st.error("El enlace no parece ser una Playlist válida.")
