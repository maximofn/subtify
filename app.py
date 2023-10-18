import gradio as gr
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import soundfile as sf
import numpy as np
import os
# import torch

SAMPLE_RATE = 8000

def get_sample_rate(audio_file_path):
    _, sample_rate = sf.read(audio_file_path, always_2d=True)
    return sample_rate

def change_sample_rate(input_audio_file_path, output_audio_file_path, sample_rate):
    # do ffmpeg -i $input_audio_file_path -ar $sample_rate $output_audio_file_path
    os.system(f'ffmpeg -i {input_audio_file_path} -ar {sample_rate} {output_audio_file_path}')

def audio_is_stereo(audio_file_path):
    audio, _ = sf.read(audio_file_path, always_2d=True)
    return audio.shape[1] == 2

def set_mono(input_audio_file_path, output_audio_file_path):
    os.system(f'ffmpeg -i {input_audio_file_path} -ac 1 {output_audio_file_path}')

os.system('wget https://maximofn.com/wp-content/uploads/2023/10/vocals.wav')
input = "vocals.wav"
input_8k = "vocals_8k.wav"
input_8k_mono = "vocals_8k_mono.wav"

sr = get_sample_rate(input)

if sr != SAMPLE_RATE:
    change_sample_rate(input, input_8k, SAMPLE_RATE)
else:
    input_8k = input

if audio_is_stereo(input_8k):
    set_mono(input_8k, input_8k_mono)
else:
    input_8k_mono = input_8k

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'
separation = pipeline(Tasks.speech_separation, model='damo/speech_mossformer_separation_temporal_8k', device=device)
print("Separating...")
result = separation(input_8k_mono)
print("Separated!")

print("Saving...")
for i, signal in enumerate(result['output_pcm_list']):
    save_file = f'output_spk{i}.wav'
    sf.write(save_file, np.frombuffer(signal, dtype=np.int16), SAMPLE_RATE)
print("Saved!")


with gr.Blocks() as demo:
    gr.Textbox("Subtify")

demo.launch()
