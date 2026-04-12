import streamlit as st
import os
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Configuración de página estilo "Dark Mode" Profesional
st.set_page_config(page_title="YouTube Playlist Manager", page_icon="🎵", layout="wide")

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def extraer_id(url):
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else url

def obtener_nombres(playlist_id):
    if not API_KEY: return ["Error: Configura tu API_KEY"]
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    canciones = []
    try:
        request = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50
        )
        response = request.execute()
        for item in response['items']:
            title = item['snippet']['title']
            clean = title.split(' (')[0].split(' [')[0].replace('Lyrics', '').strip()
            canciones.append(clean)
        return canciones
    except Exception as e:
        return [f"Error: {str(e)}"]

# --- INTERFAZ ---
st.title("🎵 Gestor de Inventario Musical")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Agregar Nueva Lista")
    url_input = st.text_input("Pega el enlace de la Playlist aquí:", placeholder="https://www.youtube.com/playlist?list=...")
    
    if st.button("Procesar y Ver Canciones"):
        if url_input:
            p_id = extraer_id(url_input)
            with st.spinner("Consultando API de YouTube..."):
                lista_nombres = obtener_nombres(p_id)
                st.session_state['temp_list'] = lista_nombres
                st.success(f"Se encontraron {len(lista_nombres)} canciones.")
        else:
            st.warning("Por favor, pega un enlace válido.")

with col2:
    st.subheader("Vista Previa")
    if 'temp_list' in st.session_state:
        # Mostramos los datos en una tabla tipo Excel (como te gusta)
        st.table(st.session_state['temp_list'])

# Botón para guardar en el archivo del repo
if st.button("🚀 Confirmar y Guardar en listas.txt"):
    if url_input:
        with open("listas.txt", "a") as f:
            f.write(f"\n{url_input}")
        st.balloons()
        st.info("Enlace añadido a listas.txt. El proceso de GitHub Actions lo procesará pronto.")
