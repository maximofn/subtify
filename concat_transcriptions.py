import argparse
import re
from tqdm import tqdm

def sum_seconds(time, seconds):
    # Get time in seconds
    time = time.split(",")
    time_milisecons = time[1]
    time_milisecons = int(time_milisecons)/1000
    time = time[0].split(":")
    time = int(time[0])*3600 + int(time[1])*60 + int(time[2])

    # Get integer and decimal part of seconds
    seconds, seconds_miliseconds = divmod(seconds, 1)
    seconds = int(seconds)
    seconds_miliseconds = round(seconds_miliseconds, 3)

    # Add seconds
    time = time + seconds
    time_milisecons = time_milisecons + seconds_miliseconds
    if time_milisecons >= 1:
        time = time + 1
        time_milisecons = time_milisecons - 1
        time_milisecons = round(time_milisecons, 3)

    # Get time in hh:mm:ss,mmm format
    hours = int(time) // 3600
    minutes = (int(time) % 3600) // 60
    seconds = (int(time) % 3600) % 60
    time_milisecons = str(time_milisecons).split(".")[1]
    time = f"{hours:02d}:{minutes:02d}:{seconds:02d},{time_milisecons}"

    return time

def hmsms_to_seconds(time):
    # Get time in seconds
    time = time.split(",")
    milisecons = time[1]
    time = time[0].split(":")
    time = int(time[0])*3600 + int(time[1])*60 + int(time[2])
    time = time + int(milisecons)/1000

    return time

def concatenate_transcriptions(chunk_files, seconds):
    chunk_folder = "transcriptions"
    output_folder = "concatenated_transcriptions"
    transcription_extension = "srt"

    # Read chunk files
    with open(chunk_files, "r") as f:
        files = f.read().splitlines()
    
    # Concatenate transcriptions
    transcription = ""
    num_transcriptions = 1
    progress_bar = tqdm(total=len(files), desc='Concatenating transcriptions progress')
    for i, file in enumerate(files):
        chunk = file
        _, file = chunk.split("/")
        file, _ = file.split(".")
        transcription_chunk_file = f"{chunk_folder}/{file}.{transcription_extension}"
        with open(transcription_chunk_file, "r") as f:
            transcription_chunk = f.read().splitlines()
        for line in transcription_chunk:

            # if line is dd:dd:dd,ddd --> dd:dd:dd,ddd
            if re.match(r"\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d", line):
                # Get start time (dd:dd:dd,ddd) and end time (dd:dd:dd,ddd)
                start, end = line.split(" --> ")
                # Add seconds to start and end time
                start = sum_seconds(start, i*seconds)
                end = sum_seconds(end, i*seconds)
                # Add to transcription
                transcription += f"{start} --> {end}\n"
            
            # if line is a number and carriage return --> number
            elif re.match(r"\d+$", line):
                transcription += f"{num_transcriptions}\n"
                num_transcriptions += 1
            
            else:
                transcription += f"{line}\n"
        progress_bar.update(1)
    
    # Write transcription
    file_split = file.split("_")[:-1]
    file = "_".join(file_split)
    output_file = f"{output_folder}/{file}.{transcription_extension}"
    with open(output_file, "w") as f:
        f.write(transcription)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk_files", help="Path to the file containing the paths to the chunk files")
    parser.add_argument("seconds", help="Duration of each chunk in seconds")
    args = parser.parse_args()

    chunk_files = args.chunk_files
    seconds = int(args.seconds)
    concatenate_transcriptions(chunk_files, seconds)
