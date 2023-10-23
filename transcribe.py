import os
import argparse

def main(args):
    audio_file = args.input
    language = args.language
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
    parser.add_argument('input', help='Input audio file')
    parser.add_argument('language', help='Language of the audio file')
    args = parser.parse_args()
    main(args)