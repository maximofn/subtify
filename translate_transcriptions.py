import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from lang_list import LANGUAGE_NAME_TO_CODE, WHISPER_LANGUAGES
import argparse
import re
from tqdm import tqdm

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
    
    # Translate
    translate_transcription = ""
    progress_bar = tqdm(total=len(transcription), desc='Translating transcription progress')
    for line in transcription:
        if re.match(r"\d+$", line):
            translate_transcription += f"{line}\n"
        elif re.match(r"\d\d:\d\d:\d\d,\d+ --> \d\d:\d\d:\d\d,\d+", line):
            translate_transcription += f"{line}\n"
        elif re.match(r"^$", line):
            translate_transcription += f"{line}\n"
        else:
            translated = translate(line, source_languaje, target_languaje, translate_model, translate_tokenizer, device)
            # translated = line
            translate_transcription += f"{translated}\n"
        progress_bar.update(1)
    
    # Save translation
    output_file = f"{output_folder}/{transcription_file_name}_{target_languaje}.srt"
    with open(output_file, "w") as f:
        f.write(translate_transcription)

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
