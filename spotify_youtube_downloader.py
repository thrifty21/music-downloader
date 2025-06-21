import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Spotify API credentials — replace with your own!
SPOTIFY_CLIENT_ID = 'your_spotify_client_id'
SPOTIFY_CLIENT_SECRET = 'your_spotify_client_secret'

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
                'album': album_name
            })
        elif "album" in url:
            album = sp.album(url)
            album_name = album['name']
            for item in album['tracks']['items']:
                tracks.append({
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'album': album_name
                })
        elif "playlist" in url:
            results = sp.playlist_tracks(url)
            for item in results['items']:
                track = item['track']
                album_name = track['album']['name'] if track.get('album') else ""
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': album_name
                })
        else:
            console.print("[red]Invalid Spotify URL.[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Spotify error:[/red] {e}")
        sys.exit(1)
    return tracks


def download_from_youtube(track, download_path, audio_format):
    """Search and download track from YouTube using yt-dlp with metadata."""
    query = f"{track['artist']} - {track['name']} audio"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, f"{track['artist']} - {track['name']}.%(ext)s"),
        'quiet': True,
        'noplaylist': True,
        'ffmpeg_location': FFMPEG_PATH,
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

    with YoutubeDL(ydl_opts) as ydl:
        console.print(f"[yellow]Downloading:[/yellow] {query}")
        try:
            ydl.download([f"ytsearch1:{query}"])
        except Exception as e:
            console.print(f"[red]Failed to download:[/red] {track['name']} – {e}")


def main():
    console.print("[bold green]Spotify → YouTube Downloader[/bold green]\n")

    spotify_url = Prompt.ask("Enter Spotify track/album/playlist URL")
    download_path = Prompt.ask("Enter download folder", default=r"D:\music\music")

    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    audio_format = Prompt.ask("Choose audio format", choices=["mp3", "m4a", "flac", "wav"], default="mp3")

    console.print("\n[cyan]Fetching track data from Spotify...[/cyan]")
    tracks = get_tracks_from_url(spotify_url)

    console.print(f"[green]Found {len(tracks)} track(s). Starting download...[/green]\n")

    for track in tracks:
        download_from_youtube(track, download_path, audio_format)

    console.print("\n[bold green]✅ All downloads complete.[/bold green]")


if __name__ == "__main__":
    main()
