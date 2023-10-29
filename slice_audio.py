import os
import argparse
from tqdm import tqdm

START = 00
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
    seconds = int(args.seconds)

    # Get audio duration in seconds
    duration = float(os.popen(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}').read())
    hour, minute, second = seconds_to_hms(int(duration))

    # Number of chunks
    num_chunks = -(-int(duration) // seconds)  # Redondeo hacia arriba

    # Slice audio into seconds chunks
    hour, minute, second = seconds_to_hms(seconds) # Duration of each chunk
    output_files = []
    progress_bar = tqdm(total=num_chunks, desc="Slice audio into chunks progress")
    for chunk in range(num_chunks):
        start_time = chunk * seconds
        hour_start, minute_start, second_start = seconds_to_hms(start_time) # Start time of each chunk

        if start_time + seconds > duration:
            hour, minute, second = seconds_to_hms(duration - start_time)
        else:
            hour, minute, second = seconds_to_hms(seconds)

        output = f"{FOLDER}/{name}_chunk{chunk:003d}{extension}"

        if start_time + seconds > duration:
            command = f'ffmpeg -i {input} -ss {hour_start:02d}:{minute_start:02d}:{second_start:02d} -loglevel error {output}'
        else:
            command = f'ffmpeg -i {input} -ss {hour_start:02d}:{minute_start:02d}:{second_start:02d} -t {hour:02}:{minute:02}:{second:02} -loglevel error {output}'
        os.system(command)

        output_files.append(output)

        progress_bar.update(1)

    # write output files to a txt file
    with open(f"{FOLDER}/output_files.txt", "w") as f:
        for output_file in output_files:
            f.write(f"{output_file}\n")
    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Slice audio into smaller chunks')
    argparser.add_argument('input', help='Input audio file')
    argparser.add_argument('seconds', help='Duration of each chunk in seconds')
    args = argparser.parse_args()
    main(args)
