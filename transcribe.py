import os
import argparse
from lang_list import LANGUAGE_NAME_TO_CODE, WHISPER_LANGUAGES
from tqdm import tqdm

# For pyannote.audio diarize
from pyannote.audio import Model
model = Model.from_pretrained("pyannote/segmentation-3.0", use_auth_token="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")

language_dict = {}
# Iterate over the LANGUAGE_NAME_TO_CODE dictionary
for language_name, language_code in LANGUAGE_NAME_TO_CODE.items():
    # Extract the language code (the first two characters before the underscore)
    lang_code = language_code.split('_')[0].lower()
    
    # Check if the language code is present in WHISPER_LANGUAGES
    if lang_code in WHISPER_LANGUAGES:
        # Construct the entry for the resulting dictionary
        language_dict[language_name] = {
            "transcriber": lang_code,
            "translator": language_code
        }

def transcribe(audio_file, language, num_speakers, device):
    output_folder = "transcriptions"

    # Transcribe audio file
    model = "large-v2"
    # word_timestamps = True
    print_progress = False
    if device == "cpu":
        # I supose that I am on huggingface server
        compute_type = "float32"
    else:
        compute_type = "float16"
    fp16 = True
    batch_size = 8
    verbose = False
    min_speakers = 1
    max_speakers = num_speakers
    threads = 4
    output_format = "srt"
    hf_token = "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"
    command = f'whisperx {audio_file} --model {model} --batch_size {batch_size} --compute_type {compute_type} \
--output_dir {output_folder} --output_format {output_format} --verbose {verbose} --language {language} \
--fp16 {fp16} --threads {threads} --print_progress {print_progress} --device {device} \
--diarize --max_speakers {max_speakers} --min_speakers {min_speakers} --hf_token {hf_token}'
    os.system(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files')
    parser.add_argument('input_files', help='Input audio files')
    parser.add_argument('language', help='Language of the audio file')
    parser.add_argument('num_speakers', help='Number of speakers in the audio file')
    parser.add_argument('device', help='Device to use for PyTorch inference')
    args = parser.parse_args()

    chunks_folder = "chunks"

    with open(args.input_files, 'r') as f:
        inputs = f.read().splitlines()
    
    progress_bar = tqdm(total=len(inputs), desc="Transcribe audio files progress")
    for input in inputs:
        input_file, _ = input.split('.')
        _, input_name = input_file.split('/')
        extension = "mp3"
        file = f'{chunks_folder}/{input_name}.{extension}'
        transcribe(file, language_dict[args.language]["transcriber"], args.num_speakers, args.device)
        progress_bar.update(1)
