This script allows you to download music from Spotify by providing a track, album, or playlist URL. It works by taking the track information (artist and song name) from Spotify and searching for the closest match on YouTube to download the audio.

This tool is intended for personal use only. Please respect copyright laws and the terms of service for both Spotify and YouTube.

Features
Supports Multiple URL Types: Download individual tracks, full albums, or entire playlists from Spotify.
YouTube Sourcing: Finds the corresponding audio on YouTube to avoid direct downloads from Spotify.
Multiple Audio Formats: Choose to save your files as mp3, m4a, flac, or wav.
Metadata Embedding: Automatically embeds track metadata such as title, artist, and album name into the downloaded file.
Album Art: For MP3 files, the script fetches and embeds the album cover art.
Interactive CLI: A user-friendly command-line interface guides you through the process.
Download Progress: Displays a rich progress bar for each download, showing speed, size, and estimated time remaining.
Requirements
Python 3.x
FFmpeg: Must be installed and accessible on your system.
Python packages:
spotipy
yt-dlp
rich
mutagen
requests
python-dotenv
Setup
Clone the repository:

git clone https://github.com/thrifty21/music-downloader.git
cd music-downloader
Install Python dependencies:

pip install spotipy yt-dlp rich mutagen requests python-dotenv
Set up Spotify API Credentials:

Go to the Spotify Developer Dashboard and log in.
Click "Create App" and give it a name and description.
Once created, you will see your Client ID and Client Secret.
Create a file named .env in the root of the project directory.
Add your credentials to the .env file like this:
SPOTIFY_CLIENT_ID='YOUR_CLIENT_ID'
SPOTIFY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
Configure FFmpeg Path:

Open the spotify_youtube_downloader.py script.
Find the line: FFMPEG_PATH = r"D:\visual_studio_work\music_download\ffmpeg\bin"
Change the path to point to the bin directory of your FFmpeg installation. For example:
Windows: FFMPEG_PATH = r"C:\path\to\ffmpeg\bin"
macOS/Linux: FFMPEG_PATH = "/usr/local/bin/ffmpeg" (or wherever it is located)
Usage
Run the script from your terminal:

python spotify_youtube_downloader.py
The script will prompt you to paste one or more Spotify URLs. You can paste multiple URLs separated by a comma or on new lines. Press Enter on an empty line to proceed.

Enter the full path to the folder where you want to save your music (e.g., D:\Music).

Choose your desired audio format from the available options (mp3, m4a, flac, wav).

The script will then fetch the track details from Spotify, find the corresponding songs on YouTube, and download them to your specified directory with the correct metadata and album art.