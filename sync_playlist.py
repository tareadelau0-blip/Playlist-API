import os
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def extraer_id(texto):
    match = re.search(r"list=([a-zA-Z0-9_-]+)", texto)
    return match.group(1) if match else texto.strip()

def obtener_info_playlist(youtube, playlist_id):
    try:
        # Obtenemos el título de la playlist para nombrar el archivo
        res = youtube.playlists().list(part="snippet", id=playlist_id).execute()
        titulo = res['items'][0]['snippet']['title']
        # Limpiamos el título para que sea un nombre de archivo válido
        titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", titulo).replace(" ", "_")
        
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
                t = item['snippet']['title']
                clean = t.split(' (')[0].split(' [')[0].replace('Lyrics', '').strip()
                canciones.append(clean)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token: break
            
        return titulo_limpio, canciones
    except Exception as e:
        print(f"⚠️ Error en {playlist_id}: {e}")
        return None, []

def main():
    if not API_KEY or not os.path.exists("listas.txt"):
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Crear carpeta si no existe
    if not os.path.exists("Mis_Playlists"):
        os.makedirs("Mis_Playlists")

    with open("listas.txt", "r") as f:
        urls = f.readlines()

    for url in urls:
        pid = extraer_id(url)
        if not pid: continue
        
        nombre_archivo, canciones = obtener_info_playlist(youtube, pid)
        
        if nombre_archivo:
            ruta = f"Mis_Playlists/{nombre_archivo}.txt"
            with open(ruta, "w", encoding="utf-8") as f_out:
                for i, c in enumerate(canciones, 1):
                    f_out.write(f"{i}. {c}\n")
            print(f"✅ Generado: {ruta}")

if __name__ == "__main__":
    main()
