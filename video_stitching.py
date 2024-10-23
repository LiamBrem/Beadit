import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import os

def load_audio(audio_file):
    """Load the audio file."""
    return AudioFileClip(audio_file)

def get_sorted_video_files(video_files):
    """Sort video files by number in the filename (assuming IMG_xxx format)."""
    valid_videos = []
    
    for file_name in video_files:
        try:
            # Only include files that match the "IMG_xxx" pattern
            if file_name.startswith("IMG_"):
                # Extract the number and append the valid video file to the list
                int(file_name.split("IMG_")[-1].split('.')[0])
                valid_videos.append(file_name)
        except (IndexError, ValueError):
            # Skip files that don't match the format
            continue

    return sorted(valid_videos, key=lambda x: int(x.split("IMG_")[-1].split('.')[0]))

def select_video_file(sorted_video_files, used_videos, video_directory):
    """Select the next unused video file."""
    for video_file in sorted_video_files:
        if video_file not in used_videos:
            used_videos.add(video_file)
            return os.path.join(video_directory, video_file)
    return None

def create_video_clip(video_path, start_time, end_time):
    """Create a video clip from start_time to end_time."""
    video_clip = VideoFileClip(video_path)
    return video_clip.subclip(0, min(end_time - start_time, video_clip.duration))

def show_long_clip_segments(video_path, total_clip_duration):
    """Show segments of the long video clip over two beats."""
    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    print(f"Total duration of long clip {video_path}: {total_duration}")

    segments = []
    
    # Calculate segment duration for each of the 4 clips
    segment_duration = total_clip_duration / 4  # Each segment should be of equal length

    # Calculate spacing duration (this can be adjusted)
    spacing_duration = (total_duration - (4 * segment_duration)) / (4 - 1)  # Space them out by half the segment duration

    for i in range(4):
        # Calculate the start time for each segment with spacing
        start_time = (i * (segment_duration + spacing_duration))
        end_time = start_time + segment_duration
        
        # Ensure we do not go beyond the total duration of the clip
        if start_time < total_duration:
            segments.append(video_clip.subclip(start_time, min(end_time, total_duration)))
            print(f"Created segment from {start_time:.2f} to {end_time:.2f}")

    return concatenate_videoclips(segments) if segments else None


def add_long_clip_to_final(clips, video_path, beat_start_time, beat_end_time):
    """Add long clip segments to the final clips list."""
    long_clip = show_long_clip_segments(video_path, beat_end_time - beat_start_time)
    if long_clip:  # Check if the long clip was created successfully
        clips.append(long_clip)
        print(f"Added long clip: {video_path} to the final clips.")  # Debugging output
        return 2  # Move the index by 2 for each long clip segment (2 beats)
    else:
        print(f"No segments were created for long clip: {video_path}")  # Debugging output
    return 0

def add_video_clip_to_final(clips, video_path, start_time, end_time):
    """Add a regular video clip to the final clips list."""
    try:
        video_clip = create_video_clip(video_path, start_time, end_time)
        clips.append(video_clip)
        #print(f"Added video clip: {video_path} to the final clips.")  # Debugging output
        return 1
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")
    return 0

def stitch_clips_together(audio_file, video_files, beat_times, video_directory, long_clips):
    print("Long clips provided:", long_clips)  # Debugging output
    clips = []
    audio = load_audio(audio_file)
    sorted_video_files = get_sorted_video_files(video_files)
    used_videos = set()
    
    beat_index = 0

    while beat_index < len(beat_times) - 1:
        # Select the video for the current pattern
        video_path = select_video_file(sorted_video_files, used_videos, video_directory)
        if video_path is None:
            print("All videos have been used. Exiting.")
            break

        print(f"Selected video path: {video_path}")  # Debugging output

        

        # Check if the selected video is in long_clips
        if os.path.basename(video_path) in long_clips:
            start_time = beat_times[beat_index]
            end_time = beat_times[beat_index + 2]
            # Add long clip segments for the duration of two beats
            beat_index += add_long_clip_to_final(clips, video_path, start_time, end_time)
            #print(end_time - start_time)
        else:
            start_time = beat_times[beat_index]
            end_time = beat_times[beat_index + 1]
            # For regular clips, just use the start and end time of the beat
            beat_index += add_video_clip_to_final(clips, video_path, start_time, end_time)
            #print(end_time - start_time)

    if not clips:
        print("No clips were successfully created. Exiting.")
        return

    final_video = concatenate_videoclips(clips).set_audio(audio)
    output_path = os.path.join(video_directory, "stitched_video.mp4")
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Stitched video saved as {output_path}")
