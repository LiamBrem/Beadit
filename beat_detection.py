import librosa

def detect_beats(audio_path):
    """
    Detects beats in an audio file using librosa.

    :param audio_path: Path to the audio file (.mp3)
    :return: List of times (in seconds) where beats occur
    """
    try:
        # Load the audio file
        y, sr = librosa.load(audio_path)

        # Detect beats
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        # Use the default threshold to detect beats
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

        # Convert beat frames to time (in seconds)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        
        print(f"Detected {len(beat_times)} beats at the following times (s): {beat_times}")
        return beat_times
    except Exception as e:
        print(f"An error occurred during beat detection: {e}")
        return []

# Example usage:
if __name__ == "__main__":
    audio_file_path = input("Enter the path to the audio file: ")
    detect_beats(audio_file_path)
