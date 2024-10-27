import os
from moviepy.editor import VideoFileClip, AudioFileClip
from beat_detection import detect_beats  # Importing the function from beat_detection.py
from video_stitching import stitch_clips_together
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

def list_videos_in_folder(folder_path):
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    try:
        files = os.listdir(folder_path)
        videos = [file for file in files if file.lower().endswith(video_extensions)]
        return videos
    except FileNotFoundError:
        print(f"The folder at {folder_path} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def mov_to_mp3(input_file, output_file, silence_threshold=-50, chunk_size=10):
    try:
        # Load the video and extract the audio
        video = VideoFileClip(input_file)
        audio = video.audio

        if not audio:
            raise ValueError("No audio track found in the video file.")
        
        # Export the audio to a temporary file for processing with pydub
        temp_audio_path = output_file.replace('.mp3', '.wav')
        audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
        audio.close()
        video.close()

        # Load the audio with pydub for silence detection and trimming
        sound = AudioSegment.from_wav(temp_audio_path)
        
        # Detect non-silent parts of the audio
        nonsilent_ranges = detect_nonsilent(sound, min_silence_len=500, silence_thresh=silence_threshold)

        if nonsilent_ranges:
            # Extract audio from the first non-silent part to the end
            start_trim = nonsilent_ranges[0][0]
            trimmed_audio = sound[start_trim:]
            
            # Export the trimmed audio to MP3
            trimmed_audio.export(output_file, format="mp3")
            print(f"Audio trimmed and conversion complete: {output_file}")
        else:
            print("No non-silent parts detected; audio might be silent throughout.")
        
        # Clean up temporary file
        os.remove(temp_audio_path)
        
    except FileNotFoundError:
        print(f"File {input_file} not found.")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

def list_audio_files_in_folder(folder_path):
    audio_extensions = ('.mp3',)
    try:
        files = os.listdir(folder_path)
        audios = [file for file in files if file.lower().endswith(audio_extensions)]
        return audios
    except FileNotFoundError:
        print(f"The folder at {folder_path} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def main():
    default_folder_path = "/Users/liambrem/Desktop/Videos"
    options = ['Default Folder', 'Custom Path']
    folder_completer = WordCompleter(options)

    # Prompt the user to choose between default and custom path
    choice = prompt("Select the folder path option (Default Folder/Custom Path): ", completer=folder_completer)

    if choice == 'Default Folder':
        folder_path = default_folder_path
    elif choice == 'Custom Path':
        folder_path = prompt("Please enter the path to the folder containing videos: ")
    else:
        print("Invalid choice. Exiting.")
        return

    audio_folder_path = os.path.join(folder_path, "Audio")  # Assuming Audio is a subfolder
    
    # Get video files in the main folder
    videos = list_videos_in_folder(folder_path)
    print("Videos found:", videos)

    # Collect identifiers for long clips
    long_clips = []
    while True:
        clip_id = prompt("Enter the 4-digit number following 'IMG_' for long clips (or press Enter to finish): ")
        if clip_id:
            long_clips.append(f"IMG_{clip_id}.MOV")
        else:
            break

    print("Long clips to be processed:", long_clips)

    # Check if the Audio subfolder exists before attempting to process files
    if os.path.exists(audio_folder_path):
        audio_files = list_audio_files_in_folder(audio_folder_path)
        
        if audio_files:
            print(f"Audio file(s) already found: {audio_files}")
            # Get the first audio file found
            output_audio_path = os.path.join(audio_folder_path, audio_files[0])
        else:
            audio_videos = list_videos_in_folder(audio_folder_path)
            
            if audio_videos:
                audio_video_path = os.path.join(audio_folder_path, audio_videos[0])
                print(f"Audio source video found: {audio_video_path}")
                
                # Convert the video to MP3
                output_audio_path = os.path.splitext(audio_video_path)[0] + ".mp3"
                mov_to_mp3(audio_video_path, output_audio_path)
            else:
                print("No video files found in the /Audio folder for conversion.")
                output_audio_path = None
    else:
        print(f"The subfolder {audio_folder_path} does not exist.")
        output_audio_path = None
    
    # Proceed to detect beats if an audio file is available
    if output_audio_path:
        beat_times = detect_beats(output_audio_path).tolist()
        stitch_clips_together(output_audio_path, videos, beat_times, folder_path, long_clips)
    else:
        print("No audio file available for beat detection.")

if __name__ == "__main__":
    main()
