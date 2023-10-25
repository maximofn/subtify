from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import soundfile as sf
import numpy as np
import os
import torch
import argparse
import speechbrain as sb
from speechbrain.dataio.dataio import read_audio
from speechbrain.pretrained import SepformerSeparation as separator
import torchaudio

SAMPLE_RATE = 8000
MODEL_SPEECHBRAIN = "SPEECHBRAIN"
MODEL_MODELSCOPE = "MODELSCOPE"
# MODEL = MODEL_SPEECHBRAIN
MODEL = MODEL_MODELSCOPE

def get_sample_rate(audio_file_path):
    """
    Get the sample rate of an audio file
    Args:
        audio_file_path (str): Path to the audio file

    Returns:
        int: Sample rate of the audio file
    """
    _, sample_rate = sf.read(audio_file_path, always_2d=True)
    return sample_rate

def change_sample_rate(input_audio_file_path, output_audio_file_path, sample_rate):
    """
    Change the sample rate of an audio file
    Args:
        input_audio_file_path (str): Path to the input audio file
        output_audio_file_path (str): Path to the output audio file
        sample_rate (int): Sample rate to change to
    """
    os.system(f'ffmpeg -i {input_audio_file_path} -ar {sample_rate} -loglevel error {output_audio_file_path}')

def audio_is_stereo(audio_file_path):
    """
    Check if an audio file is stereo
    Args:
        audio_file_path (str): Path to the audio file

    Returns:
        bool: True if the audio file is stereo, False otherwise
    """
    audio, _ = sf.read(audio_file_path, always_2d=True)
    return audio.shape[1] == 2

def set_mono(input_audio_file_path, output_audio_file_path):
    """
    Set an audio file to mono
    Args:
        input_audio_file_path (str): Path to the input audio file
        output_audio_file_path (str): Path to the output audio file
    """
    os.system(f'ffmpeg -i {input_audio_file_path} -ac 1 -loglevel error {output_audio_file_path}')

def write_number_speakers_txt(output_folder, num_speakers):
    """
    Write the number of speakers in a txt file
    Args:
        output_folder (str): Path to the output folder
        num_speakers (int): Number of speakers
    """
    with open(f"{output_folder}/speakers.txt", 'w') as f:
        f.write(str(num_speakers))

def separate_vocals_speechbrain(input_audio_file_path, output_folder, model):
    file, _ = input_audio_file_path.split(".")
    _, file = file.split("/")

    est_sources = model.separate_file(path=input_audio_file_path)
    num_vocals = est_sources.shape[2]
    speakers = 0
    for i in range(num_vocals):
        save_file = f'{output_folder}/{file}_speaker{i:003d}.wav'
        torchaudio.save(save_file, est_sources[:, :, i].detach().cpu(), SAMPLE_RATE)
        speakers += 1
    
    # Write number of speakers in a txt file
    write_number_speakers_txt(output_folder, speakers)

def separate_vocals_modelscope(input_audio_file_path, output_folder, model):
    # Get input and output names
    input_name, _ = input_audio_file_path.split(".")
    input_folder, input_name = input_name.split("/")

    # Set input files with 8k sample rate and mono
    input_8k = f"{input_folder}/{input_name}_8k.wav"
    input_8k_mono = f"{input_folder}/{input_name}_8k_mono.wav"

    # Check if input has 8k sample rate, if not, change it
    sr = get_sample_rate(input_audio_file_path)
    if sr != SAMPLE_RATE:
        change_sample_rate(input, input_8k, SAMPLE_RATE)
        remove_8k = True
    else:
        input_8k = input
        remove_8k = False

    # Check if input is stereo, if yes, set it to mono
    if audio_is_stereo(input_8k):
        set_mono(input_8k, input_8k_mono)
        remove_mono = True
    else:
        input_8k_mono = input_8k
        remove_mono = False

    # Separate audio voices
    result = model(input_8k_mono)

    # Save separated audio voices
    speakers = 0
    for i, signal in enumerate(result['output_pcm_list']):
        save_file = f'{output_folder}/{input_name}_speaker{i:003d}.wav'
        sf.write(save_file, np.frombuffer(signal, dtype=np.int16), SAMPLE_RATE)
        speakers += 1
    
    # Write number of speakers in a txt file
    write_number_speakers_txt(output_folder, speakers)
    
    # Remove temporary files
    if remove_8k:
        os.remove(input_8k)
    if remove_mono:
        os.remove(input_8k_mono)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Separate speech from a stereo audio file')
    argparser.add_argument('inputs_file', type=str, help='File with the list of inputs')
    argparser.add_argument('device', type=str, help='Device to use for separation')
    args = argparser.parse_args()

    device = args.device
    if MODEL == MODEL_SPEECHBRAIN:
        if device == 'cpu':
            model = separator.from_hparams(source="speechbrain/sepformer-whamr", savedir='pretrained_models/sepformer-whamr')
        elif 'cuda' in device:
            model = separator.from_hparams(source="speechbrain/sepformer-whamr", savedir='pretrained_models/sepformer-whamr', run_opts={"device":f"{device}"})
        elif device == 'gpu':
            model = separator.from_hparams(source="speechbrain/sepformer-whamr", savedir='pretrained_models/sepformer-whamr', run_opts={"device":"cuda"})
        else:
            raise ValueError(f"Device {device} is not valid")
    elif MODEL == MODEL_MODELSCOPE:
        separation = pipeline(Tasks.speech_separation, model='damo/speech_mossformer_separation_temporal_8k', device=device)
    else:
        raise ValueError(f"Model {MODEL} is not valid")

    # Read files from input file
    with open(args.inputs_file, 'r') as f:
        inputs = f.read().splitlines()
    
    output_folder = "vocals"
    for input in inputs:
        if MODEL == MODEL_SPEECHBRAIN:
            separate_vocals_speechbrain(input, output_folder, model)
        elif MODEL == MODEL_MODELSCOPE:
            separate_vocals_modelscope(input, output_folder, separation)
        else:
            raise ValueError(f"Model {MODEL} is not valid")