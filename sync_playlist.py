import os
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

def extraer_id(texto):
    # Busca el patrón 'list=' y captura lo que sigue hasta un '&' o el final
    match = re.search(r"list=([a-zA-Z0-9_-]+)", texto)
    if match:
        return match.group(1)
    # Si no es un link, asumimos que ya es un ID (si empieza por PL, RD, etc)
    return texto.strip()

def obtener_canciones(youtube, playlist_id):
    canciones = []
    next_page_token = None
    try:
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                title = item['snippet']['title']
                # Limpieza profesional
                clean = title.split(' (')[0].split(' [')[0]
                for word in ['Lyrics', 'Official Video', 'Video Oficial', 'Lyric Video']:
                    clean = clean.replace(word, '')
                canciones.append(clean.strip())
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token: break
        return canciones
    except Exception as e:
        print(f"⚠️ Error leyendo lista {playlist_id}: {e}")
        return []

def main():
    if not API_KEY:
        print("❌ Falta YOUTUBE_API_KEY en los Secrets/Env")
        return

    # 1. Leer las listas desde el archivo de texto (Nuestra "Interfaz")
    if not os.path.exists("listas.txt"):
        print("❌ No existe el archivo listas.txt")
        return

    with open("listas.txt", "r") as f:
        lineas = f.readlines()

    ids_a_procesar = [extraer_id(linea) for linea in lineas if linea.strip()]
    
    if not ids_a_procesar:
        print("📭 No hay enlaces en listas.txt")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    todo_el_catalogo = []

    for pid in ids_a_procesar:
        print(f"🔍 Extrayendo de: {pid}")
        todo_el_catalogo.extend(obtener_canciones(youtube, pid))

    # Eliminar duplicados y ordenar
    todo_el_catalogo = sorted(list(set(todo_el_catalogo)))

    # 2. Guardar el resultado final
    with open("nombres_musica.txt", "w", encoding="utf-8") as f:
        for i, nombre in enumerate(todo_el_catalogo, 1):
            f.write(f"{i}. {nombre}\n")

    print(f"✨ Proceso terminado. {len(todo_el_catalogo)} canciones en total.")

if __name__ == "__main__":
    main()
