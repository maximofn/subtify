import argparse
import cv2
import re
from tqdm import tqdm
import os
# https://github.com/Zulko/moviepy/issues/401#issuecomment-278679961

DEBUG = False

COLOR_BLUE = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BROWN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_PURPLE = (128, 0, 128)
COLOR_GRAY = (128, 128, 128)

def replace_characters_that_opencv_cant_show(text):
    text = text.replace("á", "a")
    text = text.replace("é", "e")
    text = text.replace("í", "i")
    text = text.replace("ó", "o")
    text = text.replace("ú", "u")
    text = text.replace("ñ", "n")
    text = text.replace("Á", "A")
    text = text.replace("É", "E")
    text = text.replace("Í", "I")
    text = text.replace("Ó", "O")
    text = text.replace("Ú", "U")
    text = text.replace("Ñ", "N")
    text = text.replace("\n", "")
    text = text.replace("¿", "?")
    text = text.replace("¡", "!")
    return text

def remove_speaker_text(text):
    # If text start with "[SPEAKER_XX]: " remove it
    match = re.match(r"^\[SPEAKER_\d+\]:\s", text)
    speaker = None
    if match:
        speaker = int(match.group(0)[9:11])
        prefix_len = len(match.group(0))  # Get length of the matched text
        text = text[prefix_len:]  # Remove the matched text from the beginning
    return text, speaker

def get_filter_text_and_speaker(text, color):
    text, speaker = remove_speaker_text(text)
    if speaker is not None:
        if speaker == 0:
            color = COLOR_GREEN
        elif speaker == 1:
            color = COLOR_BLUE
        elif speaker == 2:
            color = COLOR_RED
        elif speaker == 3:
            color = COLOR_YELLOW
        elif speaker == 4:
            color = COLOR_WHITE
        elif speaker == 5:
            color = COLOR_BLACK
        elif speaker == 6:
            color = COLOR_BROWN
        elif speaker == 7:
            color = COLOR_MAGENTA
        elif speaker == 8:
            color = COLOR_ORANGE
        elif speaker == 9:
            color = COLOR_PURPLE
    return text, color

def create_dict_of_transcription(transcription_file):
    transcription_dict = {}
    
    with open(transcription_file, "r") as f:
        transcriptions = f.read().splitlines()
    
    for line in transcriptions:

        # if line is dd:dd:dd,ddd --> dd:dd:dd,ddd (start and end time) add a new key to the dictionary
        if re.match(r"\d\d:\d\d:\d\d,\d+ --> \d\d:\d\d:\d\d,\d+", line):
            # Get start time (dd:dd:dd,ddd) and end time (dd:dd:dd,ddd)
            start, end = line.split(" --> ")
            # Add key to dictionary
            transcription_dict[start] = ""
        
        # if line is a number and carriage continue
        elif re.match(r"\d+$", line):
            continue

        # if line is a carriage return continue
        elif re.match(r"^$", line):
            continue

        # if line is a transcription add it to the dictionary
        else:
            # Remove characters that opencv can't show
            line = replace_characters_that_opencv_cant_show(line)
            transcription_dict[start] += f"{line}\n"

    return transcription_dict

def hour_minute_seconds_miliseconds_to_seconds(time):
    hours, minutes, seconds_miliseconds = time.split(":")
    seconds, miliseconds = seconds_miliseconds.split(",")
    seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(miliseconds) / 1000
    return seconds

def seconds_to_hour_minute_seconds_miliseconds(seconds):
    miliseconds = str(seconds).split(".")[1]
    miliseconds = f"0.{miliseconds}"
    miliseconds = float(miliseconds)
    miliseconds = int(miliseconds * 1000)
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = (int(seconds) % 3600) % 60
    time = f"{hours:02d}:{minutes:02d}:{seconds:02d},{miliseconds:03d}"
    return time

def search_transcription_in_dict_of_transcription(transcription_dict, seconds):
    # Get list of keys
    keys = list(transcription_dict.keys())

    # Search the key in the dictionary
    for i in range(len(keys)-1):
        key_hmsms = keys[i]
        next_key_hmsms = keys[i+1]
        key_seconds = hour_minute_seconds_miliseconds_to_seconds(key_hmsms)
        next_key_seconds = hour_minute_seconds_miliseconds_to_seconds(next_key_hmsms)
        if key_seconds <= seconds and seconds < next_key_seconds:
            return transcription_dict[key_hmsms]
        else:
            continue

def get_length_of_cv2_text(text, fontFace, fontScale, thickness):
    text_size, _ = cv2.getTextSize(text, fontFace, fontScale, thickness)
    return text_size[0]

def add_subtitles_to_video(transcription_dict, input_video_file):
    # Get the name of the input and output video files
    input_video, input_video_extension = input_video_file.split(".")
    input_video_folder, input_video_name = input_video.split("/")
    output_video_folder = input_video_folder
    output_video_name = input_video_name + "_with_subtitles"
    output_video_extension = input_video_extension
    output_video_file = f"{output_video_folder}/{output_video_name}.{output_video_extension}"

    # Open the input video file
    captured_video = cv2.VideoCapture(input_video_file)
    captured_video_fps = captured_video.get(cv2.CAP_PROP_FPS)
    captured_video_width = captured_video.get(cv2.CAP_PROP_FRAME_WIDTH)
    captured_video_height = captured_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    num_frames = int(captured_video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Progress bar
    progress_bar = tqdm(total=num_frames, desc="Add subtitles to video progress")

    # Video writer
    if not DEBUG:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_video_file, fourcc, captured_video_fps, (int(captured_video_width), int(captured_video_height)))
    
    # Set font properties
    fontFace = cv2.FONT_HERSHEY_DUPLEX
    fontScale = 1
    thickness = 2
    color = (0, 255, 0)
    lineType = cv2.LINE_AA
    bottomLeftOrigin = False

    old_text = ""
    while captured_video.isOpened():
        # Read the next frame
        ret, frame = captured_video.read()
        if not ret:
            break

        # Add the text to the frame
        current_time = captured_video.get(cv2.CAP_PROP_POS_MSEC) / 1000
        text = search_transcription_in_dict_of_transcription(transcription_dict, current_time)
        if text is not None:
            if text[-1] == "\n":
                text = text[:-1]
            if text[-1] == " ":
                text = text[:-1]
        if old_text != text:
            old_text = text
        text_length = get_length_of_cv2_text(text, fontFace, fontScale, thickness)
        if text_length > captured_video_width:
            necesary_rows = int(text_length // (captured_video_width-100)+1)
            words = text.split(" ")
            number_of_words = len(words)
            words_per_row = int(number_of_words // necesary_rows)
            text = ""
            text_position = (50, int(captured_video_height)-50*(necesary_rows+1))
            rectangle_point1 = (40, text_position[1]-30)
            for i in range(number_of_words):
                if i % words_per_row == 0 and i != 0:
                    text, color = get_filter_text_and_speaker(text, color)
                    length_of_text = get_length_of_cv2_text(text, fontFace, fontScale, thickness)
                    if length_of_text > 10:
                        rectangle_point2 = (length_of_text+50, text_position[1]+10)
                        cv2.rectangle(frame, rectangle_point1, rectangle_point2, COLOR_GRAY, -1, cv2.LINE_AA, 0)
                    cv2.putText(frame, text, text_position, fontFace, fontScale, color, thickness, lineType, bottomLeftOrigin)
                    text = ""
                    text_position = (50, text_position[1]+50)
                    rectangle_point1 = (40, text_position[1]-30)
                text += words[i] + " "
            # Add the last words
            text, color = get_filter_text_and_speaker(text, color)
            length_of_text = get_length_of_cv2_text(text, fontFace, fontScale, thickness)
            if length_of_text > 10:
                rectangle_point2 = (length_of_text+50, text_position[1]+10)
                cv2.rectangle(frame, rectangle_point1, rectangle_point2, COLOR_GRAY, -1, cv2.LINE_AA, 0)
            cv2.putText(frame, text, text_position, fontFace, fontScale, color, thickness, lineType, bottomLeftOrigin)
        else:
            text_position = (50, int(captured_video_height)-50)
            rectangle_point1 = (40, text_position[1]-30)
            rectangle_point2 = (int(captured_video_width)-50, text_position[1]+10)
            if text is not None:
                text, color = get_filter_text_and_speaker(text, color)
            length_of_text = get_length_of_cv2_text(text, fontFace, fontScale, thickness)
            if length_of_text > 10:
                rectangle_point2 = (length_of_text+50, text_position[1]+10)
                cv2.rectangle(frame, rectangle_point1, rectangle_point2, COLOR_GRAY, -1, cv2.LINE_AA, 0)
                cv2.putText(frame, text, text_position, fontFace, fontScale, color, thickness, lineType, bottomLeftOrigin)
        
        # Update the progress bar
        progress_bar.update(1)

        # Show the frame
        if DEBUG:
            cv2.imshow('frame', frame)
            # Set window 520x293
            cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("frame", 520, 293)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Write the frame
        if not DEBUG:
            video.write(frame)
    
    # Release the video capture object
    captured_video.release()

    # Close all the frames
    cv2.destroyAllWindows()

    # Release the video writer object
    if not DEBUG:
        video.release()

    # Add audio to the video
    if not DEBUG:
        progress_bar = tqdm(total=3, desc="Add audio to video progress")
        command = f"ffmpeg -i {output_video_file} -i {input_audio_file} -c:v copy -c:a aac -strict experimental -loglevel warning {output_video_file}_with_audio.{output_video_extension}"
        os.system(command)
        progress_bar.update(1)
        command = f"rm {output_video_file}"
        os.system(command)
        progress_bar.update(1)
        command = f"mv {output_video_file}_with_audio.{output_video_extension} {output_video_file}"
        os.system(command)
        progress_bar.update(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("transcription_file", help="Transcribed text")
    parser.add_argument("input_video_file", help="Input video file")
    parser.add_argument("input_audio_file", help="Input audio file")
    args = parser.parse_args()

    transcription_file = args.transcription_file
    input_video_file = args.input_video_file
    input_audio_file = args.input_audio_file

    transcription_dict = create_dict_of_transcription(transcription_file)
    # for key in transcription_dict.keys():
    #     print(key)
    #     print(transcription_dict[key])
    #     print("\n\n")
    add_subtitles_to_video(transcription_dict, input_video_file)