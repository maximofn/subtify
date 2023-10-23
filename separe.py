from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import soundfile as sf
import numpy as np
import os
import torch
import argparse

SAMPLE_RATE = 8000

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
    os.system(f'ffmpeg -i {input_audio_file_path} -ar {sample_rate} {output_audio_file_path}')

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
    os.system(f'ffmpeg -i {input_audio_file_path} -ac 1 {output_audio_file_path}')

def main(args):
    # Get input and output files
    input = args.input
    output = args.input

    # Get input and output names
    input_name = input.split(".")[0]
    output_name = output.split(".")[0]

    # Get folder of output file
    input_folder = input_name.split("/")[0]
    output_folder = output_name.split("/")[0]
    input_file_name = input_name.split("/")[1]
    output_file_name = output_name.split("/")[1]

    # Set input files with 8k sample rate and mono
    input_8k = f"{input_name}_8k.wav"
    input_8k_mono = f"{input_name}_8k_mono.wav"

    # Check if input has 8k sample rate, if not, change it
    sr = get_sample_rate(input)
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
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    separation = pipeline(Tasks.speech_separation, model='damo/speech_mossformer_separation_temporal_8k', device=device)
    result = separation(input_8k_mono)

    # Save separated audio voices
    for i, signal in enumerate(result['output_pcm_list']):
        save_file = f'{output_folder}/{output_file_name}_speaker{i:003d}.wav'
        sf.write(save_file, np.frombuffer(signal, dtype=np.int16), SAMPLE_RATE)
    
    # Remove temporary files
    if remove_8k:
        os.remove(input_8k)
    if remove_mono:
        os.remove(input_8k_mono)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Separate speech from a stereo audio file')
    argparser.add_argument('input', type=str, help='Input audio file')
    args = argparser.parse_args()
    main(args)