import gradio as gr
# import os
# import torch
# from time import sleep
# from tqdm import tqdm
# import argparse
# from lang_list import union_language_dict
# # import pyperclip
# from pytube import YouTube
# import re

# NUMBER = 100
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# # DEVICE = "cpu"
# DOWNLOAD = True
# SLICE_AUDIO = False
# SEPARE_VOCALS = False
# TRANSCRIBE_AUDIO = False
# CONCATENATE_TRANSCRIPTIONS = False
# TRANSLATE_TRANSCRIPTIONS = False
# ADD_SUBTITLES_TO_VIDEO = False
# REMOVE_FILES = False
# REMOVE_ALL = False
# if SEPARE_VOCALS:
#     SECONDS = 150
# else:
#     SECONDS = 300

# YOUTUBE = "youtube"
# TWITCH = "twitch"
# ERROR = "error"

# language_dict = union_language_dict()

# def subtify_no_ui():
#     number_works = 7
#     progress_bar = tqdm(total=number_works, desc="Subtify")

#     ################## Download video and audio ##################
#     if DOWNLOAD:
#         print('*'*NUMBER)
#         # url = "https://www.twitch.tv/videos/1936119752"             # twitch Rob Mula 2 horas
#         # url = "https://www.youtube.com/watch?v=yX5EJf4R77s"         # ✅ debate, varios hablantes, 3 minutos
#         # url = "https://www.youtube.com/watch?v=cgx0QnXo1OU"         # ✅ smart home, un solo hablante, 4:42 minutos
#         url = "https://www.youtube.com/watch?v=dgOBxhi19T8"         # ✅ rob mula, muchos hablantes, 4:28 minutos
#         # url = "https://www.youtube.com/watch?v=Coj72EzmX20"         # rob mula, un solo hablante, 16 minutos
#         # url = "https://www.youtube.com/watch?v=Tqth0fKo0_g"           # Conversación short
#         print(f"Downloading video and audio from {url}")
#         python_file = "download.py"
#         command = f"python {python_file} {url}"
#         os.system(command)
#         sleep(5)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Slice audio ##################
#     if SLICE_AUDIO:
#         print('*'*NUMBER)
#         print("Slicing audio")
#         python_file = "slice_audio.py"
#         audio = "audios/download_audio.mp3"
#         command = f"python {python_file} {audio} {SECONDS}"
#         os.system(command)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Get vocals ##################
#     chunck_file = "chunks/output_files.txt"
#     print('*'*NUMBER)
#     if SEPARE_VOCALS:
#         print("Get vocals")
#         python_file = "separe_vocals.py"
#         command = f"python {python_file} {chunck_file} {DEVICE}"
#         os.system(command)
#         if REMOVE_FILES:
#             with open(chunck_file, 'r') as f:
#                 files = f.read().splitlines()
#             for file in files:
#                 command = f"rm {file}"
#                 os.system(command)
#     else:
#         print("Moving chunks")
#         folder_vocals = "vocals"
#         folder_chunck = "chunks"
#         with open(f"{folder_vocals}/speakers.txt", 'w') as f:
#             f.write(str(0))
#         if REMOVE_FILES:
#             command = f"mv {folder_chunck}/*.mp3 {folder_vocals}/"
#             os.system(command)
#         else:
#             command = f"cp {folder_chunck}/*.mp3 {folder_vocals}/"
#             os.system(command)
#     print('*'*NUMBER)
#     print("\n\n")
#     progress_bar.update(1)

#     ################# Transcript vocals ##################
#     speakers_file = "vocals/speakers.txt"
#     if TRANSCRIBE_AUDIO:
#         print('*'*NUMBER)
#         print("Transcript vocals")
#         python_file = "transcribe.py"
#         language = "English"
#         command = f"python {python_file} {chunck_file} {language} {speakers_file} {DEVICE} {not SEPARE_VOCALS}"
#         os.system(command)
#         if REMOVE_FILES:
#             vocals_folder = "vocals"
#             with open(chunck_file, 'r') as f:
#                 files = f.read().splitlines()
#             with open(speakers_file, 'r') as f:
#                 speakers = f.read().splitlines()
#                 speakers = int(speakers[0])
#             for file in files:
#                 if speakers > 0:
#                     vocals_extension = "wav"
#                     for i in range(speakers):
#                         file_name, _ = file.split(".")
#                         _, file_name = file_name.split("/")
#                         vocal = f'{vocals_folder}/{file_name}_speaker{i:003d}.{vocals_extension}'
#                         command = f"rm {vocal}"
#                         os.system(command)
#                 else:
#                     vocals_extension = "mp3"
#                     file_name, _ = file.split(".")
#                     _, file_name = file_name.split("/")
#                     vocal = f'{vocals_folder}/{file_name}.{vocals_extension}'
#                     command = f"rm {vocal}"
#                     os.system(command)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Concatenate transcriptions ##################
#     if CONCATENATE_TRANSCRIPTIONS:
#         print('*'*NUMBER)
#         print("Concatenate transcriptions")
#         python_file = "concat_transcriptions.py"
#         command = f"python {python_file} {chunck_file} {SECONDS} {speakers_file}"
#         os.system(command)
#         if REMOVE_FILES:
#             with open(chunck_file, 'r') as f:
#                 files = f.read().splitlines()
#             for file in files:
#                 file_name, _ = file.split(".")
#                 _, file_name = file_name.split("/")
#                 transcriptions_folder = "transcriptions"
#                 transcription_extension = "srt"
#                 command = f"rm {transcriptions_folder}/{file_name}.{transcription_extension}"
#                 os.system(command)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Translate transcription ##################
#     target_languaje = "Español"
#     if TRANSLATE_TRANSCRIPTIONS:
#         print('*'*NUMBER)
#         print("Translate transcription")
#         transcription_file = "concatenated_transcriptions/download_audio.srt"
#         source_languaje = "English"
#         python_file = "translate_transcriptions.py"
#         command = f"python {python_file} {transcription_file} --source_languaje {source_languaje} --target_languaje {target_languaje} --device {DEVICE}"
#         os.system(command)
#         if REMOVE_FILES:
#             command = f"rm {transcription_file}"
#             os.system(command)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Add subtitles to video ##################
#     if ADD_SUBTITLES_TO_VIDEO:
#         print('*'*NUMBER)
#         print("Add subtitles to video")
#         python_file = "add_subtitles_to_video.py"
#         transcription_file = f"translated_transcriptions/download_audio_{target_languaje}.srt"
#         input_video_file = "videos/download_video.mp4"
#         input_audio_file = "audios/download_audio.mp3"
#         command = f"python {python_file} {transcription_file} {input_video_file} {input_audio_file}"
#         os.system(command)
#         if REMOVE_FILES:
#             command = f"rm {input_video_file}"
#             os.system(command)
#             command = f"rm {input_audio_file}"
#             os.system(command)
#             command = f"rm {transcription_file}"
#             os.system(command)
#             command = f"rm chunks/output_files.txt"
#             os.system(command)
#             command = f"rm vocals/speakers.txt"
#             os.system(command)
#         print('*'*NUMBER)
#         print("\n\n")
#     progress_bar.update(1)

#     ################## Remove all ##################
#     if REMOVE_ALL:
#         command = f"rm audios/*"
#         os.system(command)
#         command = f"rm chunks/*"
#         os.system(command)
#         command = f"rm concatenated_transcriptions/*"
#         os.system(command)
#         command = f"rm transcriptions/*"
#         os.system(command)
#         command = f"rm translated_transcriptions/*"
#         os.system(command)
#         # Check if videos/download_video.mp4 exists
#         if os.path.isfile("videos/download_video.mp4"):
#             command = f"rm videos/download_video.mp4"
#             os.system(command)
#         # command = f"rm videos/*"
#         # os.system(command)
#         command = f"rm vocals/*"
#         os.system(command)

# # def copy_url_from_clipboard():
# #     return pyperclip.paste()

# def clear_video_url():
#     visible = False
#     image = gr.Image(visible=visible, scale=1)
#     source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
#     target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
#     translate_button = gr.Button(size="lg", value="translate", min_width="10px", scale=0, visible=visible)
#     original_audio = gr.Audio(label="Original audio", elem_id="original_audio", visible=visible, interactive=False)
#     original_audio_transcribed = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", interactive=False, visible=visible)
#     original_audio_translated = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", interactive=False, visible=visible)
#     return (
#         "",
#         image, 
#         source_languaje, 
#         target_languaje, 
#         translate_button, 
#         original_audio, 
#         original_audio_transcribed, 
#         original_audio_translated,
#     )

# def get_youtube_thumbnail(url):
#     yt = YouTube(url)
#     thumbnail_url = yt.thumbnail_url
#     return thumbnail_url

# def is_valid_youtube_url(url):
#     patron_youtube = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
#     if not re.match(patron_youtube, url):
#         return False
#     return True

# def is_valid_url(url):
#     source_languaje = gr.Dropdown(visible=True, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
#     target_languaje = gr.Dropdown(visible=True, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
#     translate_button = gr.Button(size="lg", value="translate", min_width="10px", scale=0, visible=True)
#     original_audio = gr.Audio(label="Original audio", elem_id="original_audio", visible=True, interactive=False)
#     original_audio_transcribed = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", interactive=False, visible=True)
#     original_audio_translated = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", interactive=False, visible=True)
#     subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=True, interactive=False)

#     # Youtube
#     if "youtube" in url.lower() or "youtu.be" in url.lower():
#         if is_valid_youtube_url(url):
#             thumbnail = get_youtube_thumbnail(url)
#             if thumbnail:
#                 return (
#                     gr.Image(value=thumbnail, visible=True, show_download_button=False, container=False), 
#                     source_languaje,
#                     target_languaje,
#                     translate_button, 
#                     gr.Textbox(value=YOUTUBE, label="Stream page", elem_id="stream_page", visible=False),
#                     original_audio,
#                     original_audio_transcribed, 
#                     original_audio_translated,
#                     subtitled_video
#                 )
#             else:
#                 return (
#                     gr.Image(value="assets/youtube-no-thumbnails.webp", visible=True, show_download_button=False, container=False), 
#                     source_languaje,
#                     target_languaje,
#                     translate_button, 
#                     gr.Textbox(value=YOUTUBE, label="Stream page", elem_id="stream_page", visible=False),
#                     original_audio,
#                     original_audio_transcribed, 
#                     original_audio_translated,
#                     subtitled_video
#                 )
    
#     # Twitch
#     elif "twitch" in url.lower() or "twitch.tv" in url.lower():
#         return (
#             gr.Image(value="assets/twitch.webp", visible=True, show_download_button=False, container=False), 
#             source_languaje,
#             target_languaje,
#             translate_button, 
#             gr.Textbox(value=TWITCH, label="Stream page", elem_id="stream_page", visible=False),
#             original_audio,
#             original_audio_transcribed, 
#             original_audio_translated,
#             subtitled_video
#         )
    
#     # Error
#     visible = False
#     image = gr.Image(value="assets/youtube_error.webp", visible=visible, show_download_button=False, container=False)
#     source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
#     target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
#     translate_button = gr.Button(size="lg", value="translate", min_width="10px", scale=0, visible=visible)
#     stream_page = gr.Textbox(value=ERROR, label="Stream page", elem_id="stream_page", visible=visible)
#     original_audio = gr.Audio(label="Original audio", elem_id="original_audio", visible=visible, interactive=False)
#     original_audio_transcribed = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", interactive=False, visible=visible)
#     original_audio_translated = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", interactive=False, visible=visible)
#     subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=visible, interactive=False)
#     return (
#         image, 
#         source_languaje,
#         target_languaje,
#         translate_button, 
#         stream_page,
#         original_audio,
#         original_audio_transcribed, 
#         original_audio_translated,
#         subtitled_video
#     )

# def get_audio_and_video_from_video(url, stream_page):
#     python_file = "download.py"
#     command = f"python {python_file} {url}"
#     os.system(command)
#     # sleep(5)

#     audio = "audios/download_audio.mp3"
#     video = "videos/download_video.mp4"

#     return (
#         gr.Audio(value=audio, label="Original audio", elem_id="original_audio", visible=True, interactive=False),
#         gr.Textbox(value=audio, label="Original audio path", elem_id="original_audio_path", visible=False),
#         gr.Textbox(value=video, label="Original video path", elem_id="original_video_path", visible=False)
#     )

# def trascribe_audio(audio_path, source_languaje):
#     python_file = "slice_audio.py"
#     command = f"python {python_file} {audio_path} {SECONDS}"
#     os.system(command)

#     folder_vocals = "vocals"
#     folder_chunck = "chunks"
#     with open(f"{folder_vocals}/speakers.txt", 'w') as f:
#         f.write(str(0))
#     command = f"mv {folder_chunck}/*.mp3 {folder_vocals}/"
#     os.system(command)

#     python_file = "transcribe.py"
#     chunck_file = "chunks/output_files.txt"
#     speakers_file = "vocals/speakers.txt"
#     command = f"python {python_file} {chunck_file} {source_languaje} {speakers_file} {DEVICE} {not SEPARE_VOCALS}"
#     os.system(command)
#     with open(chunck_file, 'r') as f:
#         files = f.read().splitlines()
#     with open(speakers_file, 'r') as f:
#         speakers = f.read().splitlines()
#         speakers = int(speakers[0])
#     for file in files:
#         if speakers > 0:
#             vocals_extension = "wav"
#             for i in range(speakers):
#                 file_name, _ = file.split(".")
#                 _, file_name = file_name.split("/")
#                 vocal = f'{folder_vocals}/{file_name}_speaker{i:003d}.{vocals_extension}'
#                 command = f"rm {vocal}"
#                 os.system(command)
#         else:
#             vocals_extension = "mp3"
#             file_name, _ = file.split(".")
#             _, file_name = file_name.split("/")
#             vocal = f'{folder_vocals}/{file_name}.{vocals_extension}'
#             command = f"rm {vocal}"
#             os.system(command)

#     python_file = "concat_transcriptions.py"
#     command = f"python {python_file} {chunck_file} {SECONDS} {speakers_file}"
#     os.system(command)
#     with open(chunck_file, 'r') as f:
#         files = f.read().splitlines()
#     for file in files:
#         file_name, _ = file.split(".")
#         _, file_name = file_name.split("/")
#         transcriptions_folder = "transcriptions"
#         transcription_extension = "srt"
#         command = f"rm {transcriptions_folder}/{file_name}.{transcription_extension}"
#         os.system(command)

#     audio_transcribed = "concatenated_transcriptions/download_audio.srt"
#     with open(audio_transcribed, 'r') as f:
#         result = f.read()

#     return (
#         result,
#         gr.Textbox(value=audio_transcribed, label="Original audio transcribed", elem_id="original_audio_transcribed", visible=False)
#     )

# def translate_transcription(original_audio_transcribed_path, source_languaje, target_languaje):
#     python_file = "translate_transcriptions.py"
#     command = f"python {python_file} {original_audio_transcribed_path} --source_languaje {source_languaje} --target_languaje {target_languaje} --device {DEVICE}"
#     os.system(command)

#     translated_transcription = f"translated_transcriptions/download_audio_{target_languaje}.srt"
#     with open(translated_transcription, 'r') as f:
#         result = f.read()
#     transcription_file = "concatenated_transcriptions/download_audio.srt"
#     command = f"rm {transcription_file}"
#     os.system(command)

#     return (
#         result,
#         gr.Textbox(value=translated_transcription, label="Original audio translated", elem_id="original_audio_translated", visible=False)
#     )

# def add_translated_subtitles_to_video(original_video_path, original_audio_path, original_audio_translated_path):
#     python_file = "add_subtitles_to_video.py"
#     command = f"python {python_file} {original_audio_translated_path} {original_video_path} {original_audio_path}"
#     os.system(command)

#     command = f"rm {original_video_path}"
#     os.system(command)
#     command = f"rm {original_audio_path}"
#     os.system(command)
#     command = f"rm {original_audio_translated_path}"
#     os.system(command)
#     command = f"rm chunks/output_files.txt"
#     os.system(command)
#     command = f"rm vocals/speakers.txt"
#     os.system(command)

#     subtitled_video = "videos/download_video_with_subtitles.mp4"
    
#     return gr.Video(value=subtitled_video, label="Subtitled video", elem_id="subtitled_video", visible=True, interactive=False)

def subtify():
    with gr.Blocks() as demo:
        # Layout
        gr.Markdown("""# Subtify""")
        # with gr.Row(variant="panel"):
        #     url_textbox = gr.Textbox(placeholder="Add video URL here", label="Video URL", elem_id="video_url", scale=1, interactive=True)
        #     copy_button   = gr.Button(size="sm", icon="icons/copy.svg",   value="", min_width="10px", scale=0)
        #     delete_button = gr.Button(size="sm", icon="icons/delete.svg", value="", min_width="10px", scale=0)

        # stream_page = gr.Textbox(label="Stream page", elem_id="stream_page", visible=False)
        # visible = False
        # with gr.Row(equal_height=False):
        #     image = gr.Image(visible=visible, scale=1)
        #     with gr.Column():
        #         with gr.Row():
        #             source_languaje = gr.Dropdown(visible=visible, label="Source languaje", show_label=True, value="English", choices=language_dict, scale=1, interactive=True)
        #             target_languaje = gr.Dropdown(visible=visible, label="Target languaje", show_label=True, value="Español", choices=language_dict, scale=1, interactive=True)
        #         with gr.Row():
        #             subtify_button = gr.Button(size="lg", value="subtify", min_width="10px", scale=0, visible=visible)

        # original_audio = gr.Audio(label="Original audio", elem_id="original_audio", visible=visible, interactive=False)
        # original_audio_path = gr.Textbox(label="Original audio path", elem_id="original_audio_path", visible=False)
        # original_video_path = gr.Textbox(label="Original video path", elem_id="original_video_path", visible=False)
        # original_audio_transcribed = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", interactive=False, visible=visible)
        # original_audio_transcribed_path = gr.Textbox(label="Original audio transcribed", elem_id="original_audio_transcribed", visible=False)
        # original_audio_translated = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", interactive=False, visible=visible)
        # original_audio_translated_path = gr.Textbox(label="Original audio translated", elem_id="original_audio_translated", visible=False)
        # subtitled_video = gr.Video(label="Subtitled video", elem_id="subtitled_video", visible=visible, interactive=False)

        # # Events
        # # copy_button.click(fn=copy_url_from_clipboard, outputs=url_textbox)
        # delete_button.click(
        #     fn=clear_video_url, 
        #     outputs=[
        #         url_textbox, 
        #         image, 
        #         source_languaje, 
        #         target_languaje, 
        #         subtify_button, 
        #         original_audio, 
        #         original_audio_transcribed, 
        #         original_audio_translated,
        #     ]
        # )
        # url_textbox.change(
        #     fn=is_valid_url, 
        #     inputs=url_textbox, 
        #     outputs=[
        #         image, 
        #         source_languaje, 
        #         target_languaje, 
        #         subtify_button, 
        #         stream_page, 
        #         original_audio, 
        #         original_audio_transcribed, 
        #         original_audio_translated,
        #         subtitled_video
        #     ]
        # )
        # subtify_button.click(fn=get_audio_and_video_from_video, inputs=[url_textbox, stream_page], outputs=[original_audio, original_audio_path, original_video_path])
        # original_audio.change(fn=trascribe_audio, inputs=[original_audio_path, source_languaje], outputs=[original_audio_transcribed, original_audio_transcribed_path])
        # original_audio_transcribed.change(fn=translate_transcription, inputs=[original_audio_transcribed_path, source_languaje, target_languaje], outputs=[original_audio_translated, original_audio_translated_path])
        # original_audio_translated.change(fn=add_translated_subtitles_to_video, inputs=[original_video_path, original_audio_path, original_audio_translated_path], outputs=subtitled_video)


    demo.launch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_ui", action="store_true")
    args = parser.parse_args()

    if args.no_ui:
        subtify_no_ui()
    else:
        subtify()