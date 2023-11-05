import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from lang_list import LANGUAGE_NAME_TO_CODE, WHISPER_LANGUAGES
import argparse
import re
from tqdm import tqdm

MAX_LENGTH = 500
MAGIC_STRING = "[$&]"
DEBUG = False

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

def translate(transcribed_text, source_languaje, target_languaje, translate_model, translate_tokenizer, device="cpu"):
    # Get source and target languaje codes
    source_languaje_code = language_dict[source_languaje]["translator"]
    target_languaje_code = language_dict[target_languaje]["translator"]

    encoded = translate_tokenizer(transcribed_text, return_tensors="pt").to(device)
    generated_tokens = translate_model.generate(
        **encoded,
        forced_bos_token_id=translate_tokenizer.lang_code_to_id[target_languaje_code]
    )
    translated = translate_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

    return translated

def main(transcription_file, source_languaje, target_languaje, translate_model, translate_tokenizer, device):
    output_folder = "translated_transcriptions"
    _, transcription_file_name = transcription_file.split("/")
    transcription_file_name, _ = transcription_file_name.split(".")

    # Read transcription
    with open(transcription_file, "r") as f:
        transcription = f.read().splitlines()
    
    # Concatenate transcriptions
    raw_transcription = ""
    progress_bar = tqdm(total=len(transcription), desc='Concatenate transcriptions progress')
    for line in transcription:
        if re.match(r"\d+$", line):
            pass
        elif re.match(r"\d\d:\d\d:\d\d,\d+ --> \d\d:\d\d:\d\d,\d+", line):
            pass
        elif re.match(r"^$", line):
            pass
        else:
            line = re.sub(r"\[SPEAKER_\d\d\]:", MAGIC_STRING, line)
            raw_transcription += f"{line} "
        progress_bar.update(1)
    progress_bar.close()
    
    # Save raw transcription
    if DEBUG:
        output_file = f"{output_folder}/{transcription_file_name}_raw.srt"
        with open(output_file, "w") as f:
            f.write(raw_transcription)

    # Split raw transcription
    raw_transcription_list = raw_transcription.split(MAGIC_STRING)
    if raw_transcription_list[0] == "":
        raw_transcription_list = raw_transcription_list[1:]

    # Concatenate transcripts and translate when length is less than MAX_LENGTH
    translated_transcription = ""
    concatenate_transcription = raw_transcription_list[0] + MAGIC_STRING
    progress_bar = tqdm(total=len(raw_transcription_list), desc='Translate transcriptions progress')
    progress_bar.update(1)
    if len(raw_transcription_list) > 1:
        for transcription in raw_transcription_list[1:]:
            if len(concatenate_transcription) + len(transcription) < MAX_LENGTH:
                concatenate_transcription += transcription + MAGIC_STRING
            else:
                translation = translate(concatenate_transcription, source_languaje, target_languaje, translate_model, translate_tokenizer, device)
                translated_transcription += translation
                concatenate_transcription = transcription + MAGIC_STRING
            progress_bar.update(1)
        # Translate last part
        translation = translate(concatenate_transcription, source_languaje, target_languaje, translate_model, translate_tokenizer, device)
        translated_transcription += translation
    else:
        translated_transcription = translate(concatenate_transcription, source_languaje, target_languaje, translate_model, translate_tokenizer, device)
    progress_bar.close()
    
    # Save translated transcription raw
    if DEBUG:
        output_file = f"{output_folder}/{transcription_file_name}_{target_languaje}_raw.srt"
        with open(output_file, "w") as f:
            f.write(translated_transcription)
    
    # Read transcription
    with open(transcription_file, "r") as f:
        transcription = f.read().splitlines()

    # Add time stamps
    translated_transcription_time_stamps = ""
    translated_transcription_list = translated_transcription.split(MAGIC_STRING)
    progress_bar = tqdm(total=len(translated_transcription_list), desc='Add time stamps to translated transcriptions progress')
    i = 0
    for line in transcription:
        if re.match(r"\d+$", line):
            translated_transcription_time_stamps += f"{line}\n"
        elif re.match(r"\d\d:\d\d:\d\d,\d+ --> \d\d:\d\d:\d\d,\d+", line):
            translated_transcription_time_stamps += f"{line}\n"
        elif re.match(r"^$", line):
            translated_transcription_time_stamps += f"{line}\n"
        else:
            if (i < len(translated_transcription_list)):
                if len(translated_transcription_list[i]) > 0:
                    if translated_transcription_list[i][0] == " ": # Remove space at the beginning
                        translated_transcription_list[i] = translated_transcription_list[i][1:]
                speaker = ""
                if re.match(r"\[SPEAKER_\d\d\]:", line):
                    speaker = re.match(r"\[SPEAKER_\d\d\]:", line).group(0)
                translated_transcription_time_stamps += f"{speaker} {translated_transcription_list[i]}\n"
                i += 1
                progress_bar.update(1)
    progress_bar.close()
    
    # Save translated transcription
    output_file = f"{output_folder}/{transcription_file_name}_{target_languaje}.srt"
    with open(output_file, "w") as f:
        f.write(translated_transcription_time_stamps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("transcription_file", help="Transcribed text")
    parser.add_argument("--source_languaje", type=str, required=True)
    parser.add_argument("--target_languaje", type=str, required=True)
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    transcription_file = args.transcription_file
    source_languaje = args.source_languaje
    target_languaje = args.target_languaje
    device = args.device

    # model
    print("Loading translation model")
    translate_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt").to(device)
    translate_tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    print("Translation model loaded")

    main(transcription_file, source_languaje, target_languaje, translate_model, translate_tokenizer, device)
