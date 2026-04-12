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
    st.error(f"Falta configuración: {e}")
    st.stop()

st.set_page_config(page_title="Music Engine Pro", page_icon="⚡", layout="wide")

# --- DISEÑO UI MODERNO (CSS) ---
st.markdown("""
    <style>
    /* Fondo y fuente global */
    .main { background-color: #0d1117; color: #c9d1d9; }
    
    /* Estilo de Tarjetas Modernas */
    .st-emotion-cache-1r6slb0 {
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        background-color: #161b22;
    }

    /* Botones Profesionales */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #58a6ff;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #58a6ff;
        background-color: #30363d;
        color: #ffffff;
    }

    /* Headers */
    h1, h2, h3 { color: #f0f6fc; font-weight: 700; }
    
    /* Personalización de métricas */
    [data-testid="stMetricValue"] { color: #58a6ff; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.markdown("### 🔐 Autenticación")
    password = st.text_input("Ingresar Token de Acceso", type="password")
    st.divider()
    st.caption("Music Playlist v1.0")
    st.caption("Ref: System of Music List.")

if password != PASSWORD_APP:
    st.warning("🔒 Acceso restringido. Introduzca credenciales.")
    st.stop()

# --- FUNCIONES DE NÚCLEO ---
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
    except: pass
    return None, None, None

def actualizar_listas_en_github(nuevo_enlace):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/listas.txt"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json(); sha = data['sha']
        contenido = base64.b64decode(data['content']).decode('utf-8')
        if nuevo_enlace.strip() in contenido: return "duplicado"
        nuevo_contenido = contenido.strip() + f"\n{nuevo_enlace}"
    else: nuevo_contenido = nuevo_enlace; sha = None

    payload = {"message": "Web Sync Update", "content": base64.b64encode(nuevo_contenido.encode('utf-8')).decode('utf-8'), "sha": sha if sha else ""}
    return requests.put(url, headers=headers, json=payload).status_code in [200, 201]

# --- DASHBOARD PRINCIPAL ---
st.title("⚡ Data Terminal")
st.markdown(f"`Repository: {REPO_NAME}`")

# Fila de métricas estilo Panel de Control
status, conclusion, last_update = obtener_estado_github()
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.metric("ENGINE STATUS", status.upper() if status else "OFFLINE")
with m_col2:
    st.metric("LAST OUTCOME", conclusion.upper() if conclusion else "IDLE")
with m_col3:
    st.metric("LAST ACTIVITY", last_update.split("T")[0] if last_update else "N/A")

st.divider()

# Sección de Operaciones
c1, c2 = st.columns([1.2, 0.8], gap="large")

with c1:
    with st.expander("📥 INGRESO DE DATOS", expanded=True):
        st.write("Vincular nueva Playlist de YouTube al inventario:")
        enlace = st.text_input("URL de la Playlist", placeholder="https://...")
        if st.button("CONFIRMAR Y SUBIR"):
            if "list=" in enlace:
                if actualizar_listas_en_github(enlace):
                    st.success("Registro actualizado en GitHub.")
                    st.balloons()
                else: st.error("Fallo en la conexión remota.")
            else: st.error("URL no reconocida como lista.")

with c2:
    with st.container():
        st.subheader("⚙️ PROCESAMIENTO")
        st.write("Forzar actualización de metadata y limpieza de nombres:")
        if st.button("RUN SYNC ENGINE"):
            if disparar_sync_github():
                st.toast("Proceso iniciado...")
                time.sleep(1); st.rerun()
        
        st.markdown("---")
        # Monitor dinámico
        if status in ["in_progress", "queued"]:
            st.info("🔄 Procesando en la nube... por favor espere.")
            if st.button("RECARGAR ESTADO"): st.rerun()
        elif conclusion == "success":
            st.success("Sistema Sincronizado")
        elif conclusion == "failure":
            st.error("Error en última ejecución")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Crtiss Leejs Pedons Hermaosz © 2026 | Clouding Music Automation")
