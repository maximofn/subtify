from pytube import YouTube
import os
import argparse
import twitchdl.commands as twitch_downloader
import twitchdl.twitch
from twitchdl.commands.download import _parse_playlists

VIDEO_FOLDER = 'videos'
AUDIO_FOLDER = 'audios'

DOWNLOAD_VIDEO_NAME = 'download_video'
DOWNLOAD_AUDIO_NAME = 'download_audio'

DOWNLOAD_VIDEO_FORMAT = 'mp4'
DOWNLOAD_AUDIO_FORMAT = 'mp3'

DOWNLOAD_VIDEO = 'video'
DOWNLOAD_AUDIO = 'audio'

def download_twitch(url, type):
    # Create a new parser for the download command
    argparser = argparse.ArgumentParser(description='Download twitch video from URL')
    argparser.add_argument('--auth-token', default=None, help='Twitch auth token')
    argparser.add_argument('--chapter', default=None, help='Chapter to download')
    argparser.add_argument('--debug', default=False, help='Debug', action='store_true')
    argparser.add_argument('--end', default=None, help='End')
    argparser.add_argument('--format', default=f'{DOWNLOAD_VIDEO_FORMAT}', help='Format')
    argparser.add_argument('--keep', default=False, help='Keep', action='store_true')
    argparser.add_argument('--max_workers', default=5, help='Max workers')
    argparser.add_argument('--no_color', default=False, help='No color', action='store_true')
    argparser.add_argument('--no_join', default=False, help='No join', action='store_true')
    argparser.add_argument('--output', default=f'{VIDEO_FOLDER}/{DOWNLOAD_VIDEO_NAME}.{format}', help='Output')
    argparser.add_argument('--overwrite', default=False, help='Overwrite', action='store_true')
    argparser.add_argument('--quality', default=None, help='Quality')
    argparser.add_argument('--rate_limit', default=None, help='Rate limit')
    argparser.add_argument('--start', default=None, help='Start')
    argparser.add_argument('--version', default=False, help='Version', action='store_true')
    argparser.add_argument('videos', default=[url], help='Videos', nargs='+')
    args = argparser.parse_args()

    # Get qualitys
    access_token = twitchdl.twitch.get_access_token(1942562640, None)
    playlists_m3u8 = twitchdl.twitch.get_playlists(1942562640, access_token)
    playlists = list(_parse_playlists(playlists_m3u8))
    qualitys = [name for (name, _, _) in playlists]

    # Select quality
    if type == DOWNLOAD_VIDEO:
        args.quality = qualitys[0]
        args.format = DOWNLOAD_VIDEO_FORMAT
        args.output = f'{VIDEO_FOLDER}/{DOWNLOAD_VIDEO_NAME}.{args.format}'
    elif type == DOWNLOAD_AUDIO:
        args.quality = qualitys[-1]
        args.format = "mkv"
        args.output = f'{AUDIO_FOLDER}/{DOWNLOAD_AUDIO_NAME}.{args.format}'

    # Download
    twitch_downloader.download(args)
    if type == DOWNLOAD_AUDIO:
        os.system(f'ffmpeg -i {AUDIO_FOLDER}/{DOWNLOAD_AUDIO_NAME}.{args.format} -c:a libmp3lame -b:a 192k -stats -loglevel warning {AUDIO_FOLDER}/{DOWNLOAD_AUDIO_NAME}.{DOWNLOAD_AUDIO_FORMAT}')
        os.system(f'rm {AUDIO_FOLDER}/{DOWNLOAD_AUDIO_NAME}.{args.format}')

def download_youtube_video(url, type):
    # yt = YouTube(url)
    # yt.streams.filter(only_audio=True).first().download()
    pass

def main(args):
    url = args.url
    if 'twitch' in url.lower():
        download_twitch(url, DOWNLOAD_VIDEO)
        download_twitch(url, DOWNLOAD_AUDIO)
    elif 'youtube' in url.lower() or 'youtu.be' in url.lower():
        download_youtube_video(url)
    else:
        print('Unknown video source')

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Download video from URL')
    argparser.add_argument('url', help='URL of video')
    args = argparser.parse_args()
    main(args)