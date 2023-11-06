import gradio as gr
import argparse
import sys
import os
import torch
from time import sleep
from tqdm import tqdm
from lang_list import union_language_dict
# import pyperclip
from pytube import YouTube
import re
import transformers

NUMBER = 100
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# DEVICE = "cpu"
DOWNLOAD = True
SLICE_AUDIO = True
SEPARE_VOCALS = False
TRANSCRIBE_AUDIO = True
CONCATENATE_TRANSCRIPTIONS = True
TRANSLATE_TRANSCRIPTIONS = True
ADD_SUBTITLES_TO_VIDEO = True
REMOVE_FILES = False
if DEVICE == "cpu":
    # I supose that I am on huggingface server
    SECONDS = 300
else:
    SECONDS = 300

YOUTUBE = "youtube"
TWITCH = "twitch"
ERROR = "error"

language_dict = union_language_dict()

def subtify_no_ui():
    number_works = 7
    progress_bar = tqdm(total=number_works, desc="Subtify")
    folder_vocals = "vocals"
    folder_chunck = "chunks"
    folder_concatenated = "concatenated_transcriptions"
    folder_translated_transcriptions = "translated_transcriptions"
    if not os.path.exists(folder_vocals):
        os.makedirs(folder_vocals)
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
        # url = "https://www.youtube.com/watch?v=yX5EJf4R77s"         # ✅ debate, varios hablantes, 3 minutos
        # url = "https://www.youtube.com/watch?v=cgx0QnXo1OU"         # ✅ smart home, un solo hablante, 4:42 minutos
        url = "https://www.youtube.com/watch?v=dgOBxhi19T8"         # ✅ rob mula, muchos hablantes, 4:28 minutos
        # url = "https://www.youtube.com/watch?v=Coj72EzmX20"         # rob mula, un solo hablante, 16 minutos
        # url = "https://www.youtube.com/watch?v=Tqth0fKo0_g"           # Conversación short
        print(f"Downloading video and audio from {url}")
        python_file = "download.py"
        command = f"python {python_file} {url}"
        os.system(command)
        sleep(5)
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

    ################## Get vocals ##################
    chunck_file = "chunks/output_files.txt"
    print('*'*NUMBER)
    if SEPARE_VOCALS:
        print("Get vocals")
        python_file = "separe_vocals.py"
        command = f"python {python_file} {chunck_file} {DEVICE}"
        os.system(command)
        if REMOVE_FILES:
            with open(chunck_file, 'r') as f:
                files = f.read().splitlines()
            for file in files:
                command = f"rm {file}"
                os.system(command)
    else:
        print("Moving chunks")
        with open(f"{folder_vocals}/speakers.txt", 'w') as f:
            f.write(str(0))
        if REMOVE_FILES:
            command = f"mv {folder_chunck}/*.mp3 {folder_vocals}/"
            os.system(command)
        else:
            command = f"cp {folder_chunck}/*.mp3 {folder_vocals}/"
            os.system(command)
    print('*'*NUMBER)
    print("\n\n")
    progress_bar.update(1)

    ################# Transcript vocals ##################
    speakers_file = "vocals/speakers.txt"
    if TRANSCRIBE_AUDIO:
        print('*'*NUMBER)
        print("Transcript vocals")
        python_file = "transcribe.py"
        language = "English"
        command = f"python {python_file} {chunck_file} {language} {speakers_file} {DEVICE} {not SEPARE_VOCALS}"
        os.system(command)
        if REMOVE_FILES:
            vocals_folder = "vocals"
            with open(chunck_file, 'r') as f:
                files = f.read().splitlines()
            with open(speakers_file, 'r') as f:
                speakers = f.read().splitlines()
                speakers = int(speakers[0])
            for file in files:
                if speakers > 0:
                    vocals_extension = "wav"
                    for i in range(speakers):
                        file_name, _ = file.split(".")
                        _, file_name = file_name.split("/")
                        vocal = f'{vocals_folder}/{file_name}_speaker{i:003d}.{vocals_extension}'
                        command = f"rm {vocal}"
                        os.system(command)
                else:
                    vocals_extension = "mp3"
                    file_name, _ = file.split(".")
                    _, file_name = file_name.split("/")
                    vocal = f'{vocals_folder}/{file_name}.{vocals_extension}'
                    command = f"rm {vocal}"
                    os.system(command)
        print('*'*NUMBER)
        print("\n\n")
    progress_bar.update(1)

    ################## Concatenate transcriptions ##################
    if CONCATENATE_TRANSCRIPTIONS:
        print('*'*NUMBER)
        print("Concatenate transcriptions")
        python_file = "concat_transcriptions.py"
        command = f"python {python_file} {chunck_file} {SECONDS} {speakers_file}"
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

def remove_all():
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

# # def copy_url_from_clipboard():
# #     return pyperclip.paste()

def clear_video_url():
    visible = False
    image = gr.Image(visible=visible, scale=1)
    source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
    target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
    num_speaker = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    number_of_speakers = gr.Dropdown(visible=visible, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True)
    translate_button = gr.Button(size="lg", value="translate", min_width="10px", scale=0, visible=visible)
    original_audio_transcribed = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", interactive=False, visible=visible)
    original_audio_translated = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", interactive=False, visible=visible)
    return (
        "",
        image, 
        source_languaje, 
        target_languaje, 
        number_of_speakers, 
        translate_button, 
        original_audio_transcribed, 
        original_audio_translated,
    )

def get_youtube_thumbnail(url):
    yt = YouTube(url)
    thumbnail_url = yt.thumbnail_url
    return thumbnail_url

def is_valid_youtube_url(url):
    patron_youtube = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    if not re.match(patron_youtube, url):
        return False
    return True

def is_valid_url(url):
    source_languaje = gr.Dropdown(visible=True, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
    target_languaje = gr.Dropdown(visible=True, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
    num_speaker = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    number_of_speakers = gr.Dropdown(visible=True, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True)
    subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=True)
    subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=True, interactive=False)

    # Youtube
    if "youtube" in url.lower() or "youtu.be" in url.lower():
        if is_valid_youtube_url(url):
            thumbnail = get_youtube_thumbnail(url)
            if thumbnail:
                return (
                    gr.Image(value=thumbnail, visible=True, show_download_button=False, container=False), 
                    source_languaje,
                    target_languaje,
                    number_of_speakers,
                    subtify_button, 
                    subtitled_video, 
                )
            else:
                return (
                    gr.Image(value="assets/youtube-no-thumbnails.webp", visible=True, show_download_button=False, container=False), 
                    source_languaje,
                    target_languaje,
                    number_of_speakers,
                    subtify_button, 
                    subtitled_video, 
                )
    
    # Twitch
    elif "twitch" in url.lower() or "twitch.tv" in url.lower():
        return (
            gr.Image(value="assets/twitch.webp", visible=True, show_download_button=False, container=False), 
            source_languaje,
            target_languaje,
            number_of_speakers,
            subtify_button, 
            subtitled_video, 
        )
    
    # Error
    visible = False
    image = gr.Image(value="assets/youtube_error.webp", visible=visible, show_download_button=False, container=False)
    source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
    target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
    number_of_speakers = gr.Dropdown(visible=visible, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True)
    subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=visible)
    subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=visible, interactive=False),
    return (
        image, 
        source_languaje,
        target_languaje,
        number_of_speakers,
        subtify_button, 
        subtitled_video,
    )

def get_audio_and_video_from_video(url):
    python_file = "download.py"
    command = f"python {python_file} {url}"
    os.system(command)
    sleep(5)

    audio = "audios/download_audio.mp3"
    video = "videos/download_video.mp4"

    return (
        gr.Textbox(value="Ok", label="Video downloaded", elem_id="video_downloaded", interactive=False, visible=True),
        gr.Textbox(value=audio, label="Original audio path", elem_id="original_audio_path", visible=False),
        gr.Textbox(value=video, label="Original video path", elem_id="original_video_path", visible=False)
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

    with open(f"{folder_vocals}/speakers.txt", 'w') as f:
        f.write(str(0))
    command = f"mv {folder_chunck}/*.mp3 {folder_vocals}/"
    os.system(command)
    # sleep(5)

    return (
        gr.Textbox(value="Ok", label="Video sliced", elem_id="video_sliced", interactive=False, visible=True)
    )

def trascribe_audio(source_languaje):
    folder_vocals = "vocals"
    python_file = "transcribe.py"
    chunck_file = "chunks/output_files.txt"
    speakers_file = "vocals/speakers.txt"
    command = f"python {python_file} {chunck_file} {source_languaje} {speakers_file} {DEVICE} {not SEPARE_VOCALS}"
    os.system(command)
    with open(chunck_file, 'r') as f:
        files = f.read().splitlines()
    with open(speakers_file, 'r') as f:
        speakers = f.read().splitlines()
        speakers = int(speakers[0])
    for file in files:
        if speakers > 0:
            vocals_extension = "wav"
            for i in range(speakers):
                file_name, _ = file.split(".")
                _, file_name = file_name.split("/")
                vocal = f'{folder_vocals}/{file_name}_speaker{i:003d}.{vocals_extension}'
                command = f"rm {vocal}"
                os.system(command)
        else:
            vocals_extension = "mp3"
            file_name, _ = file.split(".")
            _, file_name = file_name.split("/")
            vocal = f'{folder_vocals}/{file_name}.{vocals_extension}'
            command = f"rm {vocal}"
            os.system(command)

    return (
        gr.Textbox(value="Ok", label="Video transcribed", elem_id="video_transcribed", interactive=False, visible=True)
    )

def concatenate_transcriptions():
    folder_concatenated = "concatenated_transcriptions"
    if not os.path.exists(folder_concatenated):
        os.makedirs(folder_concatenated)
    chunck_file = "chunks/output_files.txt"
    speakers_file = "vocals/speakers.txt"
    python_file = "concat_transcriptions.py"
    command = f"python {python_file} {chunck_file} {SECONDS} {speakers_file}"
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
    with open(audio_transcribed, 'r') as f:
        result = f.read()

    return (
        gr.Textbox(value="Ok", label="Transcription translated", elem_id="transcription_translated", interactive=False, visible=True),
        gr.Textbox(value=audio_transcribed, label="Original audio transcribed", elem_id="original_audio_transcribed", visible=False),
    )

def translate_transcription(original_audio_transcribed_path, source_languaje, target_languaje):
    folder_translated_transcriptions = "translated_transcriptions"
    if not os.path.exists(folder_translated_transcriptions):
        os.makedirs(folder_translated_transcriptions)
    python_file = "translate_transcriptions.py"
    command = f"python {python_file} {original_audio_transcribed_path} --source_languaje {source_languaje} --target_languaje {target_languaje} --device {DEVICE}"
    os.system(command)

    translated_transcription = f"translated_transcriptions/download_audio_{target_languaje}.srt"
    with open(translated_transcription, 'r') as f:
        result = f.read()
    transcription_file = "concatenated_transcriptions/download_audio.srt"
    command = f"rm {transcription_file}"
    os.system(command)

    return (
        gr.Textbox(value="Ok", label="Video subtitled", elem_id="video_subtitled", interactive=False, visible=True),
        gr.Textbox(value=translated_transcription, label="Original audio translated", elem_id="original_audio_translated", visible=False)
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
    command = f"rm vocals/speakers.txt"
    os.system(command)

    subtitled_video = "videos/download_video_with_subtitles.mp4"
    
    return gr.Video(value=subtitled_video, label="Subtitled video", elem_id="subtitled_video", visible=True, interactive=False)

def subtify():
    with gr.Blocks() as demo:
        # Layout
        num_speaker = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        gr.Markdown("""# Subtify""")
        with gr.Row(variant="panel"):
            url_textbox = gr.Textbox(placeholder="Add video URL here", label="Video URL", elem_id="video_url", scale=1, interactive=True)
            # copy_button   = gr.Button(size="sm", icon="icons/copy.svg",   value="", min_width="10px", scale=0)
            # delete_button = gr.Button(size="sm", icon="icons/delete.svg", value="", min_width="10px", scale=0)

        visible = False
        with gr.Row(equal_height=False):
            image = gr.Image(visible=visible, scale=1)
            with gr.Column():
                with gr.Row():
                    source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True, info="Language of the video")
                    target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True, info="Language to translate the subtitles")
                    number_of_speakers = gr.Dropdown(visible=visible, label="Number of speakers", show_label=True, value=10, choices=num_speaker, scale=1, interactive=True, info="Number of speakers in the video, if you don't know, select 10")
                with gr.Row():
                    subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=visible)

        with gr.Row():
            video_donwloaded = gr.Textbox(placeholder="Waiting", label="Video downloaded", elem_id="video_downloaded", interactive=False, visible=True)
            video_sliced = gr.Textbox(placeholder="Waiting", label="Video sliced", elem_id="video_sliced", interactive=False, visible=True)
            video_transcribed = gr.Textbox(placeholder="Waiting", label="Video transcribed", elem_id="video_transcribed", interactive=False, visible=True)
            video_translated = gr.Textbox(placeholder="Waiting", label="Transcription translated", elem_id="transcription_translated", interactive=False, visible=True)
            video_subtitled = gr.Textbox(placeholder="Waiting", label="Video subtitled", elem_id="video_subtitled", interactive=False, visible=True)

        original_audio_path = gr.Textbox(label="Original audio path", elem_id="original_audio_path", visible=False)
        original_video_path = gr.Textbox(label="Original video path", elem_id="original_video_path", visible=False)
        original_audio_transcribed_path = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", visible=False)
        original_audio_translated_path = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", visible=False)
        subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=visible, interactive=False)

        # Events
        # copy_button.click(fn=copy_url_from_clipboard, outputs=url_textbox)
        # delete_button.click(
        #     fn=clear_video_url, 
        #     outputs=[
        #         url_textbox, 
        #         image, 
        #         source_languaje, 
        #         target_languaje, 
        #         number_of_speakers, 
        #         subtify_button, 
        #         original_audio_transcribed, 
        #         original_audio_translated,
        #     ]
        # )
        url_textbox.change(
            fn=is_valid_url, 
            inputs=url_textbox, 
            outputs=[
                image, 
                source_languaje, 
                target_languaje, 
                number_of_speakers, 
                subtify_button, 
                subtitled_video,
            ]
        )
        subtify_button.click(fn=get_audio_and_video_from_video, inputs=[url_textbox], outputs=[video_donwloaded, original_audio_path, original_video_path])
        video_donwloaded.change(fn=slice_audio, inputs=[original_audio_path], outputs=[video_sliced])
        video_sliced.change(fn=trascribe_audio, inputs=[source_languaje], outputs=[video_transcribed])
        video_transcribed.change(fn=concatenate_transcriptions, inputs=[], outputs=[video_translated, original_audio_transcribed_path])
        video_translated.change(fn=translate_transcription, inputs=[original_audio_transcribed_path, source_languaje, target_languaje], outputs=[video_subtitled, original_audio_translated_path])
        video_subtitled.change(fn=add_translated_subtitles_to_video, inputs=[original_video_path, original_audio_path, original_audio_translated_path], outputs=subtitled_video)

    demo.launch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_ui", action="store_true")
    parser.add_argument("--remove_all", action="store_true")
    args = parser.parse_args()

    if args.no_ui:
        subtify_no_ui()
    elif args.remove_all:
        remove_all()
    else:
        subtify()