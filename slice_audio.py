import os
import argparse

START = 00
SECONDS = 150
FOLDER = "chunks"

def seconds_to_hms(seconds):
    hour = 00
    minute = 00
    second = seconds

    while second >= 60:
        minute += 1
        second -= 60
        while minute >= 60:
            hour += 1
            minute -= 60

    return hour, minute, second

def hms_to_seconds(hour, minute, second):
    return hour*3600 + minute*60 + second

def main(args):
    input = args.input
    # name, extension = input.split(".")
    path, filename = os.path.split(input)
    name, extension = os.path.splitext(filename)
    print(path, name, extension)

    # Get audio duration in seconds
    duration = float(os.popen(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}').read())
    hour, minute, second = seconds_to_hms(int(duration))
    print(f"Audio duration = {duration} = {hour}:{minute:02d}:{second}")

    # Number of chunks
    num_chunks = -(-int(duration) // SECONDS)  # Redondeo hacia arriba

    # Slice audio into SECONDS chunks
    hour, minute, second = seconds_to_hms(SECONDS) # Duration of each chunk
    for chunk in range(num_chunks):
        start_time = chunk * SECONDS
        hour_start, minute_start, second_start = seconds_to_hms(start_time) # Start time of each chunk

        if start_time + SECONDS > duration:
            hour, minute, second = seconds_to_hms(duration - start_time)
        else:
            hour, minute, second = seconds_to_hms(SECONDS)

        output = f"{FOLDER}/{name}_chunk{chunk:003d}{extension}"

        if start_time + SECONDS > duration:
            command = f'ffmpeg -i {input} -ss {hour_start:02d}:{minute_start:02d}:{second_start:02d} {output}'
        else:
            command = f'ffmpeg -i {input} -ss {hour_start:02d}:{minute_start:02d}:{second_start:02d} -t {hour:02}:{minute:02}:{second:02} {output}'
        print(command)
        os.system(command)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Slice audio into smaller chunks')
    argparser.add_argument('input', help='Input audio file')
    args = argparser.parse_args()
    main(args)
