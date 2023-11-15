import gradio as gr
import argparse
import os
import torch
from time import sleep
from tqdm import tqdm
from lang_list import union_language_dict
# import pyperclip
from pytube import YouTube
import re
from PIL import Image
import urllib.request

NUMBER = 100
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = "cpu"
DOWNLOAD = True
SLICE_AUDIO = True
TRANSCRIBE_AUDIO = True
CONCATENATE_TRANSCRIPTIONS = True
TRANSLATE_TRANSCRIPTIONS = True
ADD_SUBTITLES_TO_VIDEO = True
REMOVE_FILES = True
if DEVICE == "cpu":
    # I supose that I am on huggingface server
    # Get RAM space
    ram = int(os.popen("free -m | grep Mem | awk '{print $2}'").read())
    factor = 1
    SECONDS = int(ram*factor)
    print(f"RAM: {ram}, SECONDS: {SECONDS}")
else:
    # I supose that I am on my computer
    # Get VRAM space
    SECONDS = 300

YOUTUBE = "youtube"
TWITCH = "twitch"
ERROR = "error"

urllib.request.urlretrieve('https://maximofn.com/wp-content/uploads/2023/11/subtify_logo-scaled.webp', "subtify_logo.webp")
subtify_logo = Image.open("subtify_logo.webp")
subtify_logo_width, subtify_logo_height = subtify_logo.size
factor = 4
new_width = subtify_logo_width // factor
new_height = subtify_logo_height // factor

html_social_media = '''
<div style="float: right;">
    <a href="https://maximofn.com/" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style><path d="M208 80c0-26.5 21.5-48 48-48h64c26.5 0 48 21.5 48 48v64c0 26.5-21.5 48-48 48h-8v40H464c30.9 0 56 25.1 56 56v32h8c26.5 0 48 21.5 48 48v64c0 26.5-21.5 48-48 48H464c-26.5 0-48-21.5-48-48V368c0-26.5 21.5-48 48-48h8V288c0-4.4-3.6-8-8-8H312v40h8c26.5 0 48 21.5 48 48v64c0 26.5-21.5 48-48 48H256c-26.5 0-48-21.5-48-48V368c0-26.5 21.5-48 48-48h8V280H112c-4.4 0-8 3.6-8 8v32h8c26.5 0 48 21.5 48 48v64c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V368c0-26.5 21.5-48 48-48h8V288c0-30.9 25.1-56 56-56H264V192h-8c-26.5 0-48-21.5-48-48V80z"/>
        </svg>
    </a>
    <a href="http://github.com/maximofn" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 496 512">
            <style>
                svg {
                    fill: #f3f4f6;
                }
            </style>
            <path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/>
        </svg>
    </a>
    <a href="http://linkedin.com/in/MaximoFN/" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/>
        </svg>
    </a>
    <a href="http://kaggle.com/maximofn" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 320 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M304.2 501.5L158.4 320.3 298.2 185c2.6-2.7 1.7-10.5-5.3-10.5h-69.2c-3.5 0-7 1.8-10.5 5.3L80.9 313.5V7.5q0-7.5-7.5-7.5H21.5Q14 0 14 7.5v497q0 7.5 7.5 7.5h51.9q7.5 0 7.5-7.5v-109l30.8-29.3 110.5 140.6c3 3.5 6.5 5.3 10.5 5.3h66.9q5.25 0 6-3z"/>
        </svg>
    </a>
    <a href="https://twitter.com/Maximo_fn" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M389.2 48h70.6L305.6 224.2 487 464H345L233.7 318.6 106.5 464H35.8L200.7 275.5 26.8 48H172.4L272.9 180.9 389.2 48zM364.4 421.8h39.1L151.1 88h-42L364.4 421.8z"/>
        </svg>
    </a>
    <a href="https://www.instagram.com/maximo__fn/" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/>
        </svg>
    </a>
    <a href="https://www.youtube.com/channel/UCdQwg2JU_fWRsHn3yIlf3tw" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M549.655 124.083c-6.281-23.65-24.787-42.276-48.284-48.597C458.781 64 288 64 288 64S117.22 64 74.629 75.486c-23.497 6.322-42.003 24.947-48.284 48.597-11.412 42.867-11.412 132.305-11.412 132.305s0 89.438 11.412 132.305c6.281 23.65 24.787 41.5 48.284 47.821C117.22 448 288 448 288 448s170.78 0 213.371-11.486c23.497-6.321 42.003-24.171 48.284-47.821 11.412-42.867 11.412-132.305 11.412-132.305s0-89.438-11.412-132.305zm-317.51 213.508V175.185l142.739 81.205-142.739 81.201z"/>
        </svg>
    </a>
    <a href="https://www.facebook.com/profile.php?id=100085177670661" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M504 256C504 119 393 8 256 8S8 119 8 256c0 123.78 90.69 226.38 209.25 245V327.69h-63V256h63v-54.64c0-62.15 37-96.48 93.67-96.48 27.14 0 55.52 4.84 55.52 4.84v61h-31.28c-30.8 0-40.41 19.12-40.41 38.73V256h68.78l-11 71.69h-57.78V501C413.31 482.38 504 379.78 504 256z"/>
        </svg>
    </a>
    <a href="https://www.tiktok.com/@maximo__fn" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M448,209.91a210.06,210.06,0,0,1-122.77-39.25V349.38A162.55,162.55,0,1,1,185,188.31V278.2a74.62,74.62,0,1,0,52.23,71.18V0l88,0a121.18,121.18,0,0,0,1.86,22.17h0A122.18,122.18,0,0,0,381,102.39a121.43,121.43,0,0,0,67,20.14Z"/>
        </svg>
    </a>
    <a href="https://www.twitch.tv/maximofn/" rel="noopener noreferrer" aria-disabled="false" class="sm secondary  svelte-cmf5ev" id="component-1" style="flex-grow: 100;" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
            <style>
                svg {
                    fill:#f3f4f6
                }
            </style>
            <path d="M391.17,103.47H352.54v109.7h38.63ZM285,103H246.37V212.75H285ZM120.83,0,24.31,91.42V420.58H140.14V512l96.53-91.42h77.25L487.69,256V0ZM449.07,237.75l-77.22,73.12H294.61l-67.6,64v-64H140.14V36.58H449.07Z"/>
        </svg>
    </a>
</div>
'''

html_subtify_logo = f"""
<div style="display: flex; justify-content: center; align-items: center;">
    <img src='https://maximofn.com/wp-content/uploads/2023/11/subtify_logo-scaled.webp' width={new_width}px height={new_height}px >
</div>
"""

html_buy_me_a_coffe = '''
<div style="float: right;">
    <a href="https://www.buymeacoffee.com/maximofn" target="_blank">
        <img src="https://img.shields.io/badge/Buy_Me_A_Coffee-support_my_work-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white&labelColor=101010" alt="buy me a coffe">
    </a>
</div>
'''

language_dict = union_language_dict()

def subtify_no_ui():
    number_works = 6
    progress_bar = tqdm(total=number_works, desc="Subtify")
    folder_chunck = "chunks"
    folder_concatenated = "concatenated_transcriptions"
    folder_translated_transcriptions = "translated_transcriptions"
    if not os.path.exists(folder_chunck):
        os.makedirs(folder_chunck)
    if not os.path.exists(folder_concatenated):
        os.makedirs(folder_concatenated)
    if not os.path.exists(folder_translated_transcriptions):
        os.makedirs(folder_translated_transcriptions)

    ################## Download video and audio ##################
    if DOWNLOAD:
        print('*'*NUMBER)
        # url = "https://www.twitch.tv/videos/1936119752"             # twitch Rob Mula 2 horas
        url = "https://www.youtube.com/watch?v=yX5EJf4R77s"         # ✅ debate, varios hablantes, 3 minutos
        # url = "https://www.youtube.com/watch?v=cgx0QnXo1OU"         # ✅ smart home, un solo hablante, 4:42 minutos
        # url = "https://www.youtube.com/watch?v=dgOBxhi19T8"         # ✅ rob mula, muchos hablantes, 4:28 minutos
        # url = "https://www.youtube.com/watch?v=Coj72EzmX20"         # rob mula, un solo hablante, 16 minutos
        # url = "https://www.youtube.com/watch?v=Tqth0fKo0_g"           # Conversación short
        print(f"Downloading video and audio from {url}")
        python_file = "download.py"
        command = f"python {python_file} {url}"
        os.system(command)
        sleep(1)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################## Slice audio ##################
    if SLICE_AUDIO:
        print('*'*NUMBER)
        print("Slicing audio")
        python_file = "slice_audio.py"
        audio = "audios/download_audio.mp3"
        command = f"python {python_file} {audio} {SECONDS}"
        os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################# Transcript slices ##################
    if TRANSCRIBE_AUDIO:
        print('*'*NUMBER)
        print("Transcript slices")
        chunks_folder = "chunks"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)
        python_file = "transcribe.py"
        chunks_file = "chunks/output_files.txt"
        number_of_speakers = 10
        source_languaje = "English"
        command = f"python {python_file} {chunks_file} {source_languaje} {number_of_speakers} {DEVICE}"
        os.system(command)
        if REMOVE_FILES:
            with open(chunks_file, 'r') as f:
                files = f.read().splitlines()
            for file in files:
                audios_extension = "mp3"
                file_name, _ = file.split(".")
                _, file_name = file_name.split("/")
                vocal = f'{chunks_folder}/{file_name}.{audios_extension}'
                command = f"rm {vocal}"
                os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################## Concatenate transcriptions ##################
    if CONCATENATE_TRANSCRIPTIONS:
        print('*'*NUMBER)
        print("Concatenate transcriptions")
        folder_concatenated = "concatenated_transcriptions"
        if not os.path.exists(folder_concatenated):
            os.makedirs(folder_concatenated)

        chunck_file = "chunks/output_files.txt"
        python_file = "concat_transcriptions.py"
        command = f"python {python_file} {chunck_file} {SECONDS}"
        os.system(command)
        if REMOVE_FILES:
            with open(chunck_file, 'r') as f:
                files = f.read().splitlines()
            for file in files:
                file_name, _ = file.split(".")
                _, file_name = file_name.split("/")
                transcriptions_folder = "transcriptions"
                transcription_extension = "srt"
                command = f"rm {transcriptions_folder}/{file_name}.{transcription_extension}"
                os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################## Translate transcription ##################
    target_languaje = "Español"
    if TRANSLATE_TRANSCRIPTIONS:
        print('*'*NUMBER)
        print("Translate transcription")
        transcription_file = "concatenated_transcriptions/download_audio.srt"
        source_languaje = "English"
        python_file = "translate_transcriptions.py"
        command = f"python {python_file} {transcription_file} --source_languaje {source_languaje} --target_languaje {target_languaje} --device {DEVICE}"
        os.system(command)
        if REMOVE_FILES:
            command = f"rm {transcription_file}"
            os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################## Add subtitles to video ##################
    if ADD_SUBTITLES_TO_VIDEO:
        print('*'*NUMBER)
        print("Add subtitles to video")
        python_file = "add_subtitles_to_video.py"
        transcription_file = f"translated_transcriptions/download_audio_{target_languaje}.srt"
        input_video_file = "videos/download_video.mp4"
        input_audio_file = "audios/download_audio.mp3"
        command = f"python {python_file} {transcription_file} {input_video_file} {input_audio_file}"
        os.system(command)
        if REMOVE_FILES:
            command = f"rm {input_video_file}"
            os.system(command)
            command = f"rm {input_audio_file}"
            os.system(command)
            command = f"rm {transcription_file}"
            os.system(command)
            command = f"rm chunks/output_files.txt"
            os.system(command)
            command = f"rm vocals/speakers.txt"
            os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

def remove_all_files():
    command = f"rm -r audios"
    os.system(command)
    command = f"rm -r chunks"
    os.system(command)
    command = f"rm -r concatenated_transcriptions"
    os.system(command)
    command = f"rm -r transcriptions"
    os.system(command)
    command = f"rm -r translated_transcriptions"
    os.system(command)
    command = f"rm -r videos"
    os.system(command)
    command = f"rm -r vocals"
    os.system(command)

# def paste_url_from_clipboard():
#     return pyperclip.paste()

def reset_frontend():
    visible = False
    return (
        "",
        gr.Image(visible=visible), 
        gr.Dropdown(visible=visible), 
        gr.Dropdown(visible=visible), 
        gr.Dropdown(visible=visible), 
        gr.Accordion(visible=visible),
        gr.Button(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Textbox(visible=visible),
        gr.Video(visible=visible),
    )

def show_auxiliar_block1():
    return gr.Textbox(value="URL checked", visible=False)

def get_youtube_thumbnail(url):
    yt = YouTube(url)
    thumbnail_url = yt.thumbnail_url
    return thumbnail_url

def is_valid_youtube_url(url):
    # This regular expression should match the following YouTube URL formats:
    # - https://youtube.com/watch?v=video_id
    # - https://www.youtube.com/watch?v=video_id
    # - https://youtu.be/video_id
    patron_youtube = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return bool(re.match(patron_youtube, url))

def is_valid_twitch_url(url):
    # This regular expression should match the following Twitch URL formats:
    # - https://twitch.tv/channel_name
    # - https://www.twitch.tv/channel_name
    # - https://twitch.tv/videos/video_id
    twitch_pattern = r'(https?://)?(www\.)?twitch\.tv/(videos/\d+|\w+)'
    return bool(re.match(twitch_pattern, url))

def is_valid_url(url):
    num_speaker = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    source_languaje = gr.Dropdown(visible=True, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
    target_languaje = gr.Dropdown(visible=True, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
    advanced_setings = gr.Accordion(visible=True)
    number_of_speakers = gr.Dropdown(visible=True, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True)
    subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=True)

    # Youtube
    if "youtube" in url.lower() or "youtu.be" in url.lower():
        if is_valid_youtube_url(url):
            thumbnail = get_youtube_thumbnail(url)
            if thumbnail:
                return (
                    gr.Image(value=thumbnail, visible=True, show_download_button=False, container=False), 
                    source_languaje,
                    target_languaje,
                    advanced_setings,
                    number_of_speakers,
                    subtify_button, 
                )
            else:
                return (
                    gr.Image(value="assets/youtube-no-thumbnails.webp", visible=True, show_download_button=False, container=False), 
                    source_languaje,
                    target_languaje,
                    advanced_setings,
                    number_of_speakers,
                    subtify_button, 
                )
    
    # Twitch
    elif "twitch" in url.lower() or "twitch.tv" in url.lower():
        if is_valid_twitch_url(url):
            return (
                gr.Image(value="assets/twitch.webp", visible=True, show_download_button=False, container=False), 
                source_languaje,
                target_languaje,
                advanced_setings,
                number_of_speakers,
                subtify_button, 
            )
    
    # Error
    visible = False
    image = gr.Image(value="assets/youtube_error.webp", visible=visible, show_download_button=False, container=False)
    source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
    target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
    advanced_setings = gr.Accordion(visible=visible)
    number_of_speakers = gr.Dropdown(visible=visible, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True)
    subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=visible)
    return (
        image, 
        source_languaje,
        target_languaje,
        advanced_setings,
        number_of_speakers,
        subtify_button, 
    )

def change_visibility_texboxes():

    return (
        gr.Textbox(value="Done"), 
        gr.Textbox(visible=True),
        gr.Textbox(visible=True),
        gr.Textbox(visible=True),
        gr.Textbox(visible=True),
        gr.Textbox(visible=True),
        gr.Textbox(visible=True),
        gr.Textbox(visible=False),
    )

def get_audio_and_video_from_video(url):
    audios_folder = "audios"
    videos_folder = "videos"
    if not os.path.exists(audios_folder):
        os.makedirs(audios_folder)
    if not os.path.exists(videos_folder):
        os.makedirs(videos_folder)
    
    python_file = "download.py"
    command = f"python {python_file} {url}"
    os.system(command)
    sleep(1)

    audio = "audios/download_audio.mp3"
    video = "videos/download_video.mp4"

    return (
        gr.Textbox(value="Ok"),
        gr.Textbox(value=audio),
        gr.Textbox(value=video),
    )

def slice_audio(audio_path):
    folder_vocals = "vocals"
    folder_chunck = "chunks"
    if not os.path.exists(folder_vocals):
        os.makedirs(folder_vocals)
    if not os.path.exists(folder_chunck):
        os.makedirs(folder_chunck)
    
    python_file = "slice_audio.py"
    command = f"python {python_file} {audio_path} {SECONDS}"
    os.system(command)

    return (
        gr.Textbox(value="Ok")
    )

def trascribe_audio(source_languaje, number_of_speakers):
    folder_chunks = "chunks"
    python_file = "transcribe.py"
    chunks_file = "chunks/output_files.txt"
    command = f"python {python_file} {chunks_file} {source_languaje} {number_of_speakers} {DEVICE}"
    os.system(command)

    with open(chunks_file, 'r') as f:
        files = f.read().splitlines()
    for file in files:
        audios_extension = "mp3"
        file_name, _ = file.split(".")
        _, file_name = file_name.split("/")
        vocal = f'{folder_chunks}/{file_name}.{audios_extension}'
        command = f"rm {vocal}"
        os.system(command)

    return (
        gr.Textbox(value="Ok")
    )

def concatenate_transcriptions():
    folder_concatenated = "concatenated_transcriptions"
    if not os.path.exists(folder_concatenated):
        os.makedirs(folder_concatenated)

    chunck_file = "chunks/output_files.txt"
    python_file = "concat_transcriptions.py"
    command = f"python {python_file} {chunck_file} {SECONDS}"
    os.system(command)

    with open(chunck_file, 'r') as f:
        files = f.read().splitlines()
    for file in files:
        file_name, _ = file.split(".")
        _, file_name = file_name.split("/")
        transcriptions_folder = "transcriptions"
        transcription_extension = "srt"
        command = f"rm {transcriptions_folder}/{file_name}.{transcription_extension}"
        os.system(command)

    audio_transcribed = "concatenated_transcriptions/download_audio.srt"

    return (
        gr.Textbox(value="Ok"),
        gr.Textbox(value=audio_transcribed),
    )

def translate_transcription(original_audio_transcribed_path, source_languaje, target_languaje):
    folder_translated_transcriptions = "translated_transcriptions"
    if not os.path.exists(folder_translated_transcriptions):
        os.makedirs(folder_translated_transcriptions)

    python_file = "translate_transcriptions.py"
    command = f"python {python_file} {original_audio_transcribed_path} --source_languaje {source_languaje} --target_languaje {target_languaje} --device {DEVICE}"
    os.system(command)

    translated_transcription = f"translated_transcriptions/download_audio_{target_languaje}.srt"

    transcription_file = "concatenated_transcriptions/download_audio.srt"
    command = f"rm {transcription_file}"
    os.system(command)

    return (
        gr.Textbox(value="Ok"),
        gr.Textbox(value=translated_transcription)
    )

def add_translated_subtitles_to_video(original_video_path, original_audio_path, original_audio_translated_path):
    python_file = "add_subtitles_to_video.py"
    command = f"python {python_file} {original_audio_translated_path} {original_video_path} {original_audio_path}"
    os.system(command)

    command = f"rm {original_video_path}"
    os.system(command)
    command = f"rm {original_audio_path}"
    os.system(command)
    command = f"rm {original_audio_translated_path}"
    os.system(command)
    command = f"rm chunks/output_files.txt"
    os.system(command)

    subtitled_video = "videos/download_video_with_subtitles.mp4"
    
    visible = False
    return (
        gr.Video(value=subtitled_video, visible=True),
        gr.Textbox(value="Ok", visible=visible),
        gr.Textbox(value="Ok"),
    )

def hide_textbobes_progress_info():
    visible = False
    return (
        gr.Textbox(value="Waiting", visible=visible),
        gr.Textbox(value="Waiting", visible=visible),
        gr.Textbox(value="Waiting", visible=visible),
        gr.Textbox(value="Waiting", visible=visible),
        gr.Textbox(value="Waiting", visible=visible),
        gr.Textbox(value="Waiting", visible=visible),
    )

def subtify():
    with gr.Blocks() as demo:
        num_speaker = []
        for i in range(100, 0, -1):
            num_speaker.append(i)

        # Layout
        gr.Markdown(html_social_media)
        gr.Markdown("<h1 style='text-align: center;'>Subtify</h1>")
        gr.Markdown(html_subtify_logo)
        with gr.Row(variant="panel"):
            url_textbox = gr.Textbox(placeholder="Add video URL here and wait a moment", label="Video URL", elem_id="video_url", scale=1, interactive=True)
            # paste_button   = gr.Button(size="sm", icon="icons/paste.svg",   value="paste", min_width="10px", scale=0)
            delete_button = gr.Button(size="sm", icon="icons/delete.svg", value="clear", min_width="10px", scale=0)

        visible = False
        auxiliar_block1 = gr.Textbox(label="Auxiliar block 1", elem_id="auxiliar_block1", interactive=False, visible=visible)
        with gr.Row(equal_height=False):
            image = gr.Image(visible=visible, scale=1)
            with gr.Column():
                with gr.Row():
                    source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True, info="Language of the video")
                    target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True, info="Language to translate the subtitles")
                with gr.Accordion("Advanced settings", open=False, visible=visible) as Advanced_setings:
                    number_of_speakers = gr.Dropdown(visible=visible, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True, info="Number of speakers in the video, if you don't know, select 10")
                subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=visible)

        auxiliar_block2 = gr.Textbox(placeholder="Waiting", label="Auxiliar block 2", elem_id="auxiliar_block2", interactive=False, visible=visible)
        with gr.Row():
            video_donwloaded_progress_info = gr.Textbox(placeholder="Waiting", label="Video download progress info", elem_id="video_donwloaded_progress_info", interactive=False, visible=visible)
            video_sliced_progress_info = gr.Textbox(placeholder="Waiting", label="Video slice progress info", elem_id="video_sliced_progress_info", interactive=False, visible=visible)
            video_transcribed_progress_info = gr.Textbox(placeholder="Waiting", label="Transcribe progress info", elem_id="video_transcribed_progress_info", interactive=False, visible=visible)
            transcriptions_concatenated_progress_info = gr.Textbox(placeholder="Waiting", label="Concatenate progress info", elem_id="transcriptions_concatenated_progress_info", interactive=False, visible=visible)
            video_translated_progress_info = gr.Textbox(placeholder="Waiting", label="Translate progress info", elem_id="transcription_translated_progress_info", interactive=False, visible=visible)
            video_subtitled_progress_info = gr.Textbox(placeholder="Waiting", label="Video subtitle progress info", elem_id="video_subtitled_progress_info", interactive=False, visible=visible)

        original_audio_path = gr.Textbox(label="Original audio path", elem_id="original_audio_path", visible=visible)
        original_video_path = gr.Textbox(label="Original video path", elem_id="original_video_path", visible=visible)
        original_audio_transcribed_path = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", visible=visible)
        original_audio_translated_path = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", visible=visible)
        subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=visible, interactive=visible)
        auxiliar_block3 = gr.Textbox(placeholder="Waiting", label="Auxiliar block 3", elem_id="auxiliar_block3", interactive=False, visible=visible)

        # Events
        # paste_button.click(fn=paste_url_from_clipboard, outputs=url_textbox)
        delete_button.click(
            fn=reset_frontend, 
            outputs=[
                url_textbox, 
                image, 
                source_languaje, 
                target_languaje, 
                Advanced_setings,
                number_of_speakers, 
                subtify_button, 
                auxiliar_block2, 
                video_donwloaded_progress_info, 
                video_sliced_progress_info, 
                video_transcribed_progress_info, 
                transcriptions_concatenated_progress_info, 
                video_translated_progress_info, 
                video_subtitled_progress_info, 
                subtitled_video,
            ]
        )
        url_textbox.change(
            fn=show_auxiliar_block1, 
            outputs=[auxiliar_block1]
        )
        auxiliar_block1.change(
            fn=is_valid_url, 
            inputs=url_textbox, 
            outputs=[image, source_languaje, target_languaje, Advanced_setings, number_of_speakers, subtify_button]
        )
        subtify_button.click(
            fn=change_visibility_texboxes, 
            outputs=[auxiliar_block2, video_donwloaded_progress_info, video_sliced_progress_info, video_transcribed_progress_info, transcriptions_concatenated_progress_info, video_translated_progress_info, video_subtitled_progress_info, auxiliar_block1]
        )
        auxiliar_block2.change(
            fn=get_audio_and_video_from_video, 
            inputs=[url_textbox], 
            outputs=[video_donwloaded_progress_info, original_audio_path, original_video_path]
        )
        video_donwloaded_progress_info.change(
            fn=slice_audio, 
            inputs=[original_audio_path], 
            outputs=[video_sliced_progress_info]
        )
        video_sliced_progress_info.change(
            fn=trascribe_audio, 
            inputs=[source_languaje, number_of_speakers], 
            outputs=[video_transcribed_progress_info]
        )
        video_transcribed_progress_info.change(
            fn=concatenate_transcriptions, 
            outputs=[transcriptions_concatenated_progress_info, original_audio_transcribed_path]
        )
        transcriptions_concatenated_progress_info.change(
            fn=translate_transcription, 
            inputs=[original_audio_transcribed_path, source_languaje, target_languaje], 
            outputs=[video_translated_progress_info, original_audio_translated_path]
        )
        video_translated_progress_info.change(
            fn=add_translated_subtitles_to_video, 
            inputs=[original_video_path, original_audio_path, original_audio_translated_path], 
            outputs=[subtitled_video, video_subtitled_progress_info, auxiliar_block3]
        )
        auxiliar_block3.change(
            fn=hide_textbobes_progress_info, 
            outputs=[video_donwloaded_progress_info, video_sliced_progress_info, video_transcribed_progress_info, transcriptions_concatenated_progress_info, video_translated_progress_info, video_subtitled_progress_info]
        )

        gr.Markdown(html_buy_me_a_coffe)
        
    demo.launch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_ui", action="store_true")
    parser.add_argument("--remove_all_files", action="store_true")
    args = parser.parse_args()

    if args.no_ui:
        subtify_no_ui()
    elif args.remove_all_files:
        remove_all_files()
    else:
        subtify()