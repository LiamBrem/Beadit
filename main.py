import os
from moviepy.editor import VideoFileClip, AudioFileClip
from beat_detection import detect_beats  # Importing the function from beat_detection.py
from video_stitching import stitch_clips_together
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

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


if __name__ == "__main__":
    folder_path = input("Please enter the path to the folder containing videos: ")
    audio_folder_path = os.path.join(folder_path, "Audio")  # Assuming Audio is a subfolder
    
    # Get video files in the main folder
    videos = list_videos_in_folder(folder_path)
    print("Videos found:", videos)
    
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
        #beat_times = [0.9752380952380952, 1.4628571428571429, 1.9504761904761905, 2.461315192743764, 2.948934240362812, 3.436553287981859, 3.924172335600907, 4.435011337868481, 4.922630385487528, 5.410249433106576, 5.921088435374149, 6.408707482993197, 6.919546485260771, 7.4071655328798185, 7.894784580498866, 8.40562358276644, 8.893242630385487, 9.404081632653062, 9.891700680272109, 10.402539682539683, 10.89015873015873, 11.377777777777778, 11.888616780045352, 12.376235827664399, 12.863854875283447, 13.351473922902494, 13.862312925170068, 14.349931972789115, 14.837551020408164, 15.348390022675737, 15.836009070294784, 16.32362811791383, 16.834467120181404, 17.322086167800453, 17.832925170068027, 18.320544217687075, 18.83138321995465, 19.342222222222222, 19.82984126984127, 20.340680272108845, 20.82829931972789, 21.31591836734694, 21.803537414965987, 22.31437641723356, 22.825215419501134, 23.312834467120183, 23.823673469387757, 24.3112925170068, 24.822131519274375, 25.309750566893424, 25.797369614512473, 26.308208616780046, 26.81904761904762, 27.329886621315193, 27.817505668934242, 28.305124716553287, 28.81596371882086, 29.30358276643991, 29.814421768707483, 30.30204081632653, 30.789659863945577, 31.30049886621315, 31.7881179138322, 32.298956916099776, 32.78657596371882, 33.274195011337866, 33.78503401360544, 34.29587301587301, 34.78349206349206, 35.294331065759636, 35.781950113378684, 36.26956916099773, 36.78040816326531, 37.268027210884355, 37.77886621315193, 38.26648526077098, 38.75410430839002, 39.2649433106576, 39.75256235827664, 40.263401360544215, 40.751020408163264, 41.23863945578231, 41.749478458049886, 42.237097505668935, 42.72471655328798, 43.23555555555556, 43.723174603174606]
        # print(beat_times)
    
        stitch_clips_together(output_audio_path, videos, beat_times, folder_path)


    else:
        print("No audio file available for beat detection.")