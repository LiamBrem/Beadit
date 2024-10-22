import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import os

def stitch_clips_together(audio_file, video_files, beat_times):
    clips = []
    
    # Load the audio file
    audio = AudioFileClip(audio_file)

    # Calculate how long the clips should be (between 0.25s and 3s)
    min_duration = 0.25  # seconds
    max_duration = 3.0    # seconds

    # Prepare a list to store selected video files
    used_videos = set()

    # Sort video files based on the numeric value following "IMG_"
    sorted_video_files = sorted(video_files, key=lambda x: int(x.split("IMG_")[-1].split('.')[0]))

    # Initialize a variable to keep track of the current position in the beat_times
    current_beat_index = 0

    # Get the directory of the video files
    video_directory = '/Users/liambrem/Desktop/Videos'  # Update this path as needed

    while current_beat_index < len(beat_times):
        # Randomly select the duration of the next clip
        clip_duration = random.uniform(min_duration, max_duration)
        
        # Get the current beat time
        beat_time = beat_times[current_beat_index]
        
        # Find the next video (ensure it's not already used)
        video_path = None
        
        for video_file in sorted_video_files:
            if video_file not in used_videos:
                video_path = os.path.join(video_directory, video_file)
                used_videos.add(video_file)
                break
        
        if video_path is None:  # All videos have been used
            print("All videos have been used. Exiting.")
            break

        # Check if the file exists before proceeding
        if not os.path.isfile(video_path):
            print(f"Warning: The file {video_path} does not exist.")
            continue  # Skip to the next iteration
        
        try:
            # Create a video clip
            video_clip = VideoFileClip(video_path)
            # Ensure the clip length does not exceed the available clip length
            available_duration = min(video_clip.duration, clip_duration)

            # Set the audio for the clip
            video_clip = video_clip.subclip(0, available_duration).set_audio(audio)

            # Append the video clip to the list
            clips.append(video_clip)
        
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")
            continue  # Skip to the next iteration in case of error
        
        # Move to the next beat index, choosing a random step between 1 to 3 beats
        step = random.randint(1, 3)
        current_beat_index += step
    
    if not clips:  # Check if clips list is empty
        print("No clips were successfully created. Exiting.")
        return  # Exit the function if no clips were created
    
    # Concatenate all the video clips
    final_video = concatenate_videoclips(clips)

    # Set the audio for the final video (only once to avoid issues)
    final_video = final_video.set_audio(audio)

    # Export the final video
    output_path = "stitched_video.mp4"  # You can customize this
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Stitched video saved as {output_path}")
