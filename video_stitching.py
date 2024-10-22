import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import os


def load_audio(audio_file):
    return AudioFileClip(audio_file)

def get_sorted_video_files(video_files):
    return sorted(video_files, key=lambda x: int(x.split("IMG_")[-1].split('.')[0]))

def select_video_file(sorted_video_files, used_videos, video_directory):
    for video_file in sorted_video_files:
        if video_file not in used_videos:
            video_path = os.path.join(video_directory, video_file)
            used_videos.add(video_file)
            return video_path
    return None

def create_video_clip(video_path, clip_duration, audio):
    video_clip = VideoFileClip(video_path)
    available_duration = min(video_clip.duration, clip_duration)
    return video_clip.subclip(0, available_duration).set_audio(audio)

def create_flash_clips(sorted_video_files, used_videos, audio, video_directory, beat_duration):
    """Creates 4 flash clips, each lasting for a quarter of two beats."""
    flash_clips = []
    flash_duration = beat_duration / 2 / 4  # Each flash should be a quarter of two beats

    for _ in range(4):
        video_path = select_video_file(sorted_video_files, used_videos, video_directory)
        if video_path and os.path.isfile(video_path):
            try:
                flash_clip = create_video_clip(video_path, flash_duration, audio)
                flash_clips.append(flash_clip)
            except Exception as e:
                print(f"Error processing video {video_path} for flash effect: {e}")
                continue
    return flash_clips

def stitch_clips_together(audio_file, video_files, beat_times, video_directory):
    clips = []
    audio = load_audio(audio_file)
    min_duration = 0.25
    max_duration = 3.0
    used_videos = set()
    sorted_video_files = get_sorted_video_files(video_files)
    current_beat_index = 0

    # Select a random beat index for the flash sequence (ensuring it's not near the end)
    flash_start_beat = random.randint(0, len(beat_times) - 3)  # Giving 2 beats for the flash

    while current_beat_index < len(beat_times):
        # Calculate beat duration as the difference between consecutive beats
        if current_beat_index < len(beat_times) - 1:
            beat_duration = beat_times[current_beat_index + 1] - beat_times[current_beat_index]
        else:
            beat_duration = max_duration  # If it's the last beat, use a default max duration

        if current_beat_index == flash_start_beat:
            # Create flash sequence (4 clips over 2 beats)
            flash_clips = create_flash_clips(sorted_video_files, used_videos, audio, video_directory, beat_duration)
            if flash_clips:
                clips.extend(flash_clips)
                current_beat_index += 2  # Skip 2 beats after flash sequence
            continue

        # Normal video clip creation
        clip_duration = random.uniform(min_duration, max_duration)
        video_path = select_video_file(sorted_video_files, used_videos, video_directory)

        if video_path is None:
            print("All videos have been used. Exiting.")
            break

        if not os.path.isfile(video_path):
            print(f"Warning: The file {video_path} does not exist.")
            continue

        try:
            video_clip = create_video_clip(video_path, clip_duration, audio)
            clips.append(video_clip)
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")
            continue

        step = random.randint(1, 3)
        current_beat_index += step

    if not clips:
        print("No clips were successfully created. Exiting.")
        return

    final_video = concatenate_videoclips(clips).set_audio(audio)
    output_path = os.path.join(video_directory, "stitched_video.mp4")
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Stitched video saved as {output_path}")
