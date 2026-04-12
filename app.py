import streamlit as st
import os
import re
import requests
import base64
from googleapiclient.discovery import build

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Los valores se toman de Settings > Secrets en Streamlit Cloud
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GITHUB_TOKEN = st.secrets["GH_TOKEN"]
    REPO_NAME = "tareadelau0-blip/Playlist-API"
    PASSWORD_APP = st.secrets["APP_PASSWORD"]
except KeyError as e:
    st.error(f"Falta la configuración de Secret: {e}")
    st.stop()

st.set_page_config(page_title="Music Manager Pro", page_icon="🎬", layout="wide")

# --- LOGIN ---
st.sidebar.title("🔐 Acceso")
password = st.sidebar.text_input("Contraseña de Administrador", type="password")

if password != PASSWORD_APP:
    st.warning("Por favor, introduce la contraseña en el menú lateral para gestionar las listas.")
    st.stop()

# --- FUNCIONES DE GITHUB API ---

def actualizar_listas_en_github(nuevo_enlace):
    """Agrega un nuevo link al archivo listas.txt en el repositorio"""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/listas.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. Obtener el archivo actual (necesitamos el 'sha')
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        contenido_actual = base64.b64decode(data['content']).decode('utf-8')
        sha = data['sha']
        # Evitar duplicados simples
        if nuevo_enlace.strip() in contenido_actual:
            return "duplicado"
        nuevo_contenido = contenido_actual.strip() + f"\n{nuevo_enlace}"
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
    return res.status_code == 200 or res.status_code == 201

def disparar_sync_github():
    """Llama a GitHub Actions para ejecutar el script sync_playlist.py inmediatamente"""
    url = f"https://api.github.com/repos/{REPO_NAME}/actions/workflows/update.yml/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Se dispara sobre la rama main
    data = {"ref": "main"}
    
    res = requests.post(url, headers=headers, json=data)
    # 204 No Content es el éxito para esta API
    return res.status_code == 204

# --- INTERFAZ DE USUARIO ---

st.title("🎵 Panel de Control - Playlist API")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Agregar Nueva Playlist")
    enlace = st.text_input("Pega el link de YouTube aquí:", placeholder="https://www.youtube.com/playlist?list=...")

    if st.button("🚀 Guardar en Repositorio"):
        if "list=" in enlace:
            resultado = actualizar_listas_en_github(enlace)
            if resultado == True:
                st.success("✅ ¡Enlace guardado! listas.txt ha sido actualizado.")
                st.balloons()
            elif resultado == "duplicado":
                st.warning("⚠️ Este enlace ya existe en tu archivo.")
            else:
                st.error("❌ Error al subir a GitHub. Revisa tus permisos.")
        else:
            st.error("❌ El enlace no parece ser una Playlist válida.")

with col2:
    st.subheader("⚙️ Acciones de Sistema")
    st.write("Usa este botón para procesar los nombres de las canciones ahora mismo sin esperar al horario automático.")
    
    if st.button("🔄 Sincronizar Canciones Ahora"):
        with st.spinner("Despertando a GitHub Actions..."):
            if disparar_sync_github():
                st.info("🚀 ¡Proceso de sincronización iniciado! Revisa la pestaña 'Actions' en GitHub. Los archivos .txt se actualizarán en breve.")
            else:
                st.error("❌ No se pudo iniciar el proceso. Verifica que 'workflow_dispatch' esté en tu YAML y que el Token sea correcto.")

st.markdown("---")
st.caption("Sistema de gestión automatizado para Narciso Andres Pozo Marroquin - 2026")
