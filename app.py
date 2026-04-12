import streamlit as st
import requests
import base64
import time
import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Primero definimos las variables, LUEGO las usamos
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GITHUB_TOKEN = st.secrets["GH_TOKEN"]
    REPO_NAME = "tareadelau0-blip/Playlist-API"
    PASSWORD_APP = st.secrets["APP_PASSWORD"]
except KeyError as e:
    st.error(f"Falta la configuración de Secret en Streamlit Cloud: {e}")
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
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/listas.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        contenido_actual = base64.b64decode(data['content']).decode('utf-8')
        sha = data['sha']
        if nuevo_enlace.strip() in contenido_actual:
            return "duplicado"
        nuevo_contenido = contenido_actual.strip() + f"\n{nuevo_enlace}"
    else:
        nuevo_contenido = nuevo_enlace
        sha = None

    payload = {
        "message": "Update listas.txt via Streamlit",
        "content": base64.b64encode(nuevo_contenido.encode('utf-8')).decode('utf-8'),
        "sha": sha if sha else ""
    }
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

def disparar_sync_github():
    url = f"https://api.github.com/repos/{REPO_NAME}/actions/workflows/update.yml/dispatches"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.post(url, headers=headers, json={"ref": "main"})
    return res.status_code == 204

def obtener_estado_github():
    """Consulta el estado real con un timestamp para saltar la caché"""
    ts = datetime.datetime.now().timestamp()
    # Aquí es donde usamos REPO_NAME, ahora que ya existe
    url = f"https://api.github.com/repos/{REPO_NAME}/actions/runs?per_page=1&t={ts}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            run = r.json()["workflow_runs"][0]
            return run["status"], run["conclusion"]
    except:
        pass
    return None, None

# --- INTERFAZ ---
st.title("🎵 Panel de Control - Playlist API")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Agregar Nueva Playlist")
    enlace = st.text_input("Pega el link de YouTube:", placeholder="https://www.youtube.com/playlist?list=...")

    if st.button("🚀 Guardar en Repositorio"):
        if "list=" in enlace:
            resultado = actualizar_listas_en_github(enlace)
            if resultado == True:
                st.success("✅ ¡Enlace guardado!")
                st.balloons()
            elif resultado == "duplicado":
                st.warning("⚠️ Ya existe este enlace.")
            else:
                st.error("❌ Error de permisos en GitHub.")
        else:
            st.error("❌ Enlace no válido.")

with col2:
    st.subheader("⚙️ Estado del Sistema")
    
    if st.button("🔄 Sincronizar Canciones Ahora"):
        if disparar_sync_github():
            st.toast("Petición enviada...")
            time.sleep(2) # Pausa breve para que GitHub registre el inicio
            st.rerun()
    
    st.write("---")
    
    status, conclusion = obtener_estado_github()
    
    if status in ["in_progress", "queued", "requested"]:
        st.warning("⏳ GitHub está trabajando... actualizando tus archivos .txt")
        if st.button("Actualizar Vista"):
            st.rerun()
    elif status == "completed":
        if conclusion == "success":
            st.success("✅ Todo listo: Archivos actualizados correctamente.")
        else:
            st.error(f"❌ La última sincronización falló ({conclusion}).")
    else:
        st.info("Sin procesos recientes detectados.")

    st.caption(f"Último estado: {status} | Resultado: {conclusion}")

st.markdown("---")
st.caption("Administración de Sistemas de Auditoría y Regularización Exprés - Narciso Pozo 2026")
