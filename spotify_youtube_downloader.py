import os
import sys
import spotipy
from dotenv import load_dotenv
load_dotenv()
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import requests

console = Console()


# Spotify API credentials — replace with your own!
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Hardcoded ffmpeg path
FFMPEG_PATH = r"D:\visual_studio_work\music_download\ffmpeg\bin"

def get_tracks_from_url(url):
    """Extract tracks from Spotify URL, including album name."""
    tracks = []
    try:
        if "track" in url:
            track = sp.track(url)
            album_name = track['album']['name']
            tracks.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': album_name,
                'cover_url': track['album']['images'][0]['url'] if track['album'].get('images') else None
            })
        elif "album" in url:
            album = sp.album(url)
            album_name = album['name']
            for item in album['tracks']['items']:
                tracks.append({
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'album': album_name,
                    'cover_url': track['album']['images'][0]['url'] if track['album'].get('images') else None
                })
        elif "playlist" in url:
            results = sp.playlist_tracks(url)
            for item in results['items']:
                track = item['track']
                album_name = track['album']['name'] if track.get('album') else ""
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': album_name,
                    'cover_url': track['album']['images'][0]['url'] if track['album'].get('images') else None
                })
        else:
            console.print("[red]Invalid Spotify URL.[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Spotify error:[/red] {e}")
        sys.exit(1)
    return tracks


def download_from_youtube(track, download_path, audio_format):
    query = f"{track['artist']} - {track['name']} audio"
    filename = f"{track['artist']} - {track['name']}"

    console.print(f"[yellow]Searching YouTube for:[/yellow] {query}")

    # Use Rich progress bar inside a live context
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        transient=True,  # clears the bar after finish
    ) as progress:
        task_id = None  # track the task ID from progress.add_task()

        def progress_hook(d):
            nonlocal task_id
            if d['status'] == 'downloading':
                if task_id is None:
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    task_id = progress.add_task(
                        description=f"{filename}",
                        total=total_bytes
                    )
                progress.update(task_id, completed=d.get('downloaded_bytes', 0))

            elif d['status'] == 'finished' and task_id is not None:
                progress.update(task_id, completed=progress.tasks[0].total)
                console.print(f"[green]✔ Finished downloading {d.get('filename', '')}[/green]\n")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, f"{filename}.%(ext)s"),
            'quiet': True,
            'noplaylist': True,
            'ffmpeg_location': FFMPEG_PATH,
            'progress_hooks': [progress_hook],
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True
                }
            ],
            'postprocessor_args': [
                '-metadata', f'artist={track["artist"]}',
                '-metadata', f'title={track["name"]}',
                '-metadata', f'album={track["album"]}'
            ]
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{query}"])
        except Exception as e:
            console.print(f"[red]Failed to download:[/red] {track['name']} – {e}")
            return
        
        if audio_format == "mp3" and track.get("cover_url"):
            try:
                response = requests.get(track['cover_url'], timeout=10)
                response.raise_for_status()
                cover_data = response.content

                mp3_path = os.path.join(download_path, f"{filename}.mp3")

                audio = MP3(mp3_path, ID3=ID3)

                try:
                    audio.add_tags()
                except error:
                    pass  # Tags already exist

                audio.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime='image/jpeg',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=cover_data
                    )
                )
                audio.save()
                console.print(f"[green]✔ Embedded album cover in:[/green] {filename}.mp3")
            except Exception as e:
                console.print(f"[red]⚠ Failed to embed cover art:[/red] {e}")

def main():
    console.print("[bold green]Spotify → YouTube Downloader[/bold green]\n")

    while True:
        console.print("Paste one or more Spotify URLs (separated by comma or newline). Press Enter twice when done:")
        urls_input = []
        while True:
            line = input()
            if not line:
                break
            urls_input.append(line)

        raw_urls = ",".join(urls_input).replace("\n", ",")
        spotify_urls = [url.strip() for url in raw_urls.split(",") if url.strip()]
        download_path = Prompt.ask("Enter download folder", default=r"D:\music\music")

        if not os.path.isdir(download_path):
            os.makedirs(download_path)

        audio_format = Prompt.ask("Choose audio format", choices=["mp3", "m4a", "flac", "wav"], default="mp3")

        console.print("\n[cyan]Fetching track data from Spotify...[/cyan]")
        all_tracks = []
        for url in spotify_urls:
            console.print(f"\n[cyan]Fetching tracks from:[/cyan] {url}")
            tracks = get_tracks_from_url(url)
            all_tracks.extend(tracks)
        console.print(f"[green]Found {len(all_tracks)} track(s). Starting download...[/green]\n")

        for track in all_tracks:
            download_from_youtube(track, download_path, audio_format)

        console.print("\n[bold green]✅ All downloads complete.[/bold green]")

        # Ask if the user wants to continue
        continue_choice = Prompt.ask("\nDo you want to download more?", choices=["y", "n"], default="n")
        if continue_choice.lower() != "y":
            console.print("[cyan]Exiting...[/cyan]")
            break


if __name__ == "__main__":
    main()
