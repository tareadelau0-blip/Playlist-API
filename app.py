import streamlit as st
import requests
import base64
import time
import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
    GITHUB_TOKEN = st.secrets["GH_TOKEN"]
    REPO_NAME = "tareadelau0-blip/Playlist-API"
    PASSWORD_APP = st.secrets["APP_PASSWORD"]
except KeyError as e:
    st.error(f"Falta la configuración de Secret: {e}")
    st.stop()

# Configuración de página con modo ancho por defecto
st.set_page_config(
    page_title="Music Engine Pro | Dashboard", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: #00ffcc;
        border: 1px solid #444;
    }
    .stButton>button:hover {
        border: 1px solid #00ffcc;
        color: #00ffcc;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #00ffcc;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        background-color: #161b22;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3503/3503827.png", width=100)
    st.title("System Auth")
    password = st.text_input("Admin Token", type="password")
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Edition")

if password != PASSWORD_APP:
    st.info("🔒 Sistema bloqueado. Ingrese credenciales para continuar.")
    st.stop()

# --- FUNCIONES DE LOGICA (Sin cambios en tu lógica funcional) ---

def actualizar_listas_en_github(nuevo_enlace):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/listas.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        contenido_actual = base64.b64decode(data['content']).decode('utf-8')
        sha = data['sha']
        if nuevo_enlace.strip() in contenido_actual: return "duplicado"
        nuevo_contenido = contenido_actual.strip() + f"\n{nuevo_enlace}"
    else:
        nuevo_contenido = nuevo_enlace
        sha = None

    payload = {
        "message": f"Add source: {datetime.date.today()}",
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
    ts = datetime.datetime.now().timestamp()
    url = f"https://api.github.com/repos/{REPO_NAME}/actions/runs?per_page=1&t={ts}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            run = r.json()["workflow_runs"][0]
            return run["status"], run["conclusion"], run["updated_at"]
    except:
        pass
    return None, None, None

# --- INTERFAZ PRINCIPAL ---
st.title("⚡ Music Engine Data Terminal")
st.caption(f"Connected to: {REPO_NAME}")

# Fila Superior: Métricas de Estado
status, conclusion, last_update = obtener_estado_github()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Status", status.upper() if status else "OFFLINE")
with m2:
    color_res = "SUCCESS" if conclusion == "success" else "ERROR"
    st.metric("Last Result", color_res if conclusion else "WAITING")
with m3:
    # Formatear fecha si existe
    fecha = last_update.split("T")[0] if last_update else "N/A"
    st.metric("Last Sync", fecha)

st.markdown("---")

# Cuerpo Principal
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    with st.container():
        st.subheader("📥 Data Input")
        st.markdown("Añadir nuevas fuentes de datos (YouTube Playlists)")
        enlace = st.text_input("URL de origen", placeholder="https://www.youtube.com/playlist?list=...")
        
        if st.button("💾 COMMIT TO REPOSITORY"):
            if "list=" in enlace:
                with st.spinner("Pushing to GitHub..."):
                    resultado = actualizar_listas_en_github(enlace)
                    if resultado == True:
                        st.success("DATA COMMITTED")
                        st.balloons()
                    elif resultado == "duplicado":
                        st.warning("DUPLICATE ENTRY")
                    else:
                        st.error("GITHUB AUTH ERROR")
            else:
                st.error("INVALID SOURCE URL")

with col_right:
    with st.container():
        st.subheader("⚙️ System Control")
        st.markdown("Ejecución manual de procesos de limpieza y extracción")
        
        if st.button("🔄 TRIGGER SYNC ACTION"):
            if disparar_sync_github():
                st.toast("Action Triggered Successfully", icon="🚀")
                time.sleep(1)
                st.rerun()
        
        # Consola de estado interna
        st.markdown("<br>", unsafe_allow_html=True)
        if status in ["in_progress", "queued", "requested"]:
            st.warning("⚙️ SYNCING: GitHub is processing metadata...")
            if st.button("REFRESH CONSOLE"): st.rerun()
        elif status == "completed":
            if conclusion == "success":
                st.info("📋 DATABASE READY: All files updated.")
            else:
                st.error(f"❌ SYSTEM FAILURE: {conclusion}")
        else:
            st.write("Ready for next instruction.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.caption("© 2026 Narciso Andres Pozo Marroquin | Business Systems & Audit Division")
