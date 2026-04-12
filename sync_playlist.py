import os
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def extraer_id(texto):
    """Extrae el ID de la playlist de una URL o devuelve el texto si ya es un ID"""
    match = re.search(r"list=([a-zA-Z0-9_-]+)", texto)
    return match.group(1) if match else texto.strip()

def limpiar_nombre_cancion(titulo):
    """
    Limpia el título de la canción manteniendo Artista - Título,
    pero eliminando añadidos innecesarios de YouTube.
    """
    # 1. Eliminar paréntesis que contienen palabras comunes de YouTube
    # Ej: (Official Video), (Letra), (Lyrics), (Video Oficial)
    patrones_borrar = [
        r'\(.*?Official.*?\)', r'\(.*?Video.*?\)', r'\(.*?Lyric.*?\)', 
        r'\(.*?Letra.*?\)', r'\(.*?Audio.*?\)', r'\(.*?Oficial.*?\)',
        r'\[.*?\]' # Elimina cualquier cosa entre corchetes []
    ]
    
    clean = titulo
    for patron in patrones_borrar:
        clean = re.sub(patron, '', clean, flags=re.IGNORECASE)
    
    # 2. Limpiar espacios extra resultantes
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # 3. Si el nombre termina en guion o basura por el recorte, lo limpiamos
    clean = clean.rstrip('-').strip()
    
    return clean

def obtener_info_playlist(youtube, playlist_id):
    """Obtiene el título de la playlist y la lista de canciones limpias"""
    try:
        # Obtenemos metadatos de la playlist
        res = youtube.playlists().list(part="snippet", id=playlist_id).execute()
        if not res['items']:
            return None, []
            
        titulo_playlist = res['items'][0]['snippet']['title']
        # Limpiar nombre de archivo para Windows/Linux
        titulo_archivo = re.sub(r'[\\/*?:"<>|]', "", titulo_playlist).replace(" ", "_")
        
        canciones = []
        next_page_token = None
        
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                t_original = item['snippet']['title']
                # Aplicamos la nueva limpieza robusta
                t_limpio = limpiar_nombre_cancion(t_original)
                
                # Evitar agregar canciones eliminadas o privadas
                if "Deleted video" not in t_limpio and "Private video" not in t_limpio:
                    canciones.append(t_limpio)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token: 
                break
            
        return titulo_archivo, canciones
    except Exception as e:
        print(f"⚠️ Error procesando la playlist {playlist_id}: {e}")
        return None, []

def main():
    if not API_KEY:
        print("❌ Error: YOUTUBE_API_KEY no configurada.")
        return
        
    if not os.path.exists("listas.txt"):
        print("❌ Error: No existe el archivo listas.txt")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Carpeta de salida organizada
    folder_name = "Mis_Playlists"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open("listas.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        pid = extraer_id(url)
        if not pid: 
            continue
        
        print(f"⌛ Procesando: {pid}...")
        nombre_archivo, canciones = obtener_info_playlist(youtube, pid)
        
        if nombre_archivo:
            ruta = os.path.join(folder_name, f"{nombre_archivo}.txt")
            with open(ruta, "w", encoding="utf-8") as f_out:
                for i, c in enumerate(canciones, 1):
                    f_out.write(f"{i:02d}. {c}\n")
            print(f"✅ Generado: {ruta} ({len(canciones)} canciones)")

if __name__ == "__main__":
    main()
