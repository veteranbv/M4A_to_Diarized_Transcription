import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import subprocess
import wave
import numpy as np
import os
import logging
from mutagen.mp4 import MP4
from app.utils import ensure_dir, safe_file_operation

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

@safe_file_operation
def convert_to_wav(input_path, output_path):
    """
    Converts an audio file to WAV format using ffmpeg.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the converted WAV file.

    Raises:
        subprocess.CalledProcessError: If the conversion fails.
    """
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"Converted {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting file {input_path} to WAV: {e.stderr.decode().strip()}")
        raise

@safe_file_operation
def get_audio_length(file_path):
    """
    Gets the length of an audio file in seconds.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        float: The duration of the audio file in seconds.
    """
    try:
        if file_path.lower().endswith('.m4a'):
            audio = MP4(file_path)
            return audio.info.length
        elif file_path.lower().endswith('.wav'):
            with wave.open(file_path, 'rb') as audio_file:
                frames = audio_file.getnframes()
                rate = audio_file.getframerate()
                duration = frames / float(rate)
                return duration
        else:
            logging.error(f"Unsupported audio format for {file_path}")
            return 0
    except Exception as e:
        logging.error(f"Error getting audio length for {file_path}: {str(e)}")
        return 0

@safe_file_operation
def plot_waveform(wav_file, output_path, filename):
    """
    Plots the waveform of a WAV file and saves it as an image.

    Args:
        wav_file (str): Path to the WAV file.
        output_path (str): The directory to save the waveform image.
        filename (str): The filename for the saved waveform image.
    """
    try:
        with wave.open(wav_file, 'rb') as audio_file:
            signal = audio_file.readframes(-1)
            signal = np.frombuffer(signal, dtype=np.int16)
            rate = audio_file.getframerate()
            time = np.linspace(0.0, len(signal) / rate, num=len(signal))

        plt.figure(figsize=(10, 4))
        plt.plot(time, signal)
        plt.title(f"Waveform of {os.path.basename(wav_file)}")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")

        ensure_dir(output_path)
        file_path = os.path.join(output_path, filename)
        plt.savefig(file_path)
        plt.close()

        logging.info(f"Waveform plot saved to {file_path}")
    except Exception as e:
        logging.error(f"Error plotting waveform for {wav_file}: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage and testing
    test_audio_path = "./test/data/test_audio.m4a"
    test_wav_path = "./test/data/test_audio.wav"
    test_output_dir = "./test/output"

    ensure_dir(test_output_dir)

    try:
        # Test convert_to_wav
        convert_to_wav(test_audio_path, test_wav_path)
        print(f"Converted {test_audio_path} to {test_wav_path}")

        # Test get_audio_length
        m4a_length = get_audio_length(test_audio_path)
        wav_length = get_audio_length(test_wav_path)
        print(f"M4A audio length: {m4a_length:.2f} seconds")
        print(f"WAV audio length: {wav_length:.2f} seconds")

        # Test plot_waveform
        plot_waveform(test_wav_path, test_output_dir, "test_waveform.png")
        print(f"Waveform plot saved to {os.path.join(test_output_dir, 'test_waveform.png')}")

    except Exception as e:
        logging.error(f"Error during audio utils test: {str(e)}")