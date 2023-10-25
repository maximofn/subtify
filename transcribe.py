import os
import argparse

def transcribe(audio_file, language):
    output_folder = "transcriptions"

    # Transcribe audio file
    model = "large-v2"
    word_timestamps = True
    fp16 = False
    device = "cuda"
    verbose = False
    threads = 4
    output_format = "srt"
    command = f'whisper --model {model} --output_dir {output_folder} --language {language} \
--word_timestamps {word_timestamps} --fp16 {fp16} --device {device} --verbose {verbose} \
--threads {threads} --output_format {output_format} {audio_file}'
    os.system(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files')
    parser.add_argument('input_files', help='Input audio files')
    parser.add_argument('language', help='Language of the audio file')
    parser.add_argument('speakers_file', help='File with the number of speakers')
    args = parser.parse_args()

    vocals_folder = "vocals"
    extension = "wav"

    with open(args.speakers_file, 'r') as f:
        speakers = f.read().splitlines()
        speakers = int(speakers[0])

    with open(args.input_files, 'r') as f:
        inputs = f.read().splitlines()
    for input in inputs:
        input, _ = input.split('.')
        _, input_name = input.split('/')
        for i in range(speakers):
            file = f'{vocals_folder}/{input_name}_speaker{i:003d}.{extension}'
            transcribe(file, args.language)
