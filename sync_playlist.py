import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Carga variables de entorno (Localmente desde .env, en GitHub desde Secrets)
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")

def sync_playlist():
    if not API_KEY or not PLAYLIST_ID:
        print("❌ Error: No se encontraron las credenciales.")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    canciones = []
    next_page_token = None

    print(f"📡 Obteniendo canciones de la playlist: {PLAYLIST_ID}")

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=PLAYLIST_ID,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            title = item['snippet']['title']
            # Limpieza básica de títulos
            clean_title = title.split(' (')[0].split(' [')[0].strip()
            canciones.append(clean_title)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    # Escribir la lista en el archivo de texto
    with open("nombres_musica.txt", "w", encoding="utf-8") as f:
        for i, nombre in enumerate(canciones, 1):
            f.write(f"{i}. {nombre}\n")

    print(f"✅ Sincronización completa. {len(canciones)} canciones guardadas.")

if __name__ == "__main__":
    sync_playlist()
