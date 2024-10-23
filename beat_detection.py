import librosa
import numpy as np

def detect_beats(audio_path, start_bpm=120.0, tightness=100):
    """
    Detects beats in an audio file using librosa.

    :param audio_path: Path to the audio file (.mp3)
    :param start_bpm: Initial guess for the tempo estimator (in beats per minute)
    :param tightness: Tightness of beat distribution around the estimated tempo
    :return: List of times (in seconds) where beats occur
    """
    try:
        # Load the audio file
        y, sr = librosa.load(audio_path)
        
        # Detect onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)

        # Detect beats using the onset envelope
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr,
                                                start_bpm=start_bpm, 
                                                tightness=tightness, 
                                                trim=True)

        # Convert beat frames to time (in seconds)
        beat_times = librosa.frames_to_time(beats, sr=sr)

        print(f"Detected {len(beat_times)} beats")
        return beat_times
    except Exception as e:
        print(f"An error occurred during beat detection: {e}")
        return []

# Example usage:
if __name__ == "__main__":
    audio_file_path = input("Enter the path to the audio file: ")
    detect_beats(audio_file_path)
