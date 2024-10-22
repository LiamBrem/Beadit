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

def stitch_clips_together(audio_file, video_files, beat_times, video_directory):
    """Stitch video clips together based on the beat times, switching clips on each beat."""
    clips = []
    audio = load_audio(audio_file)
    sorted_video_files = get_sorted_video_files(video_files)
    used_videos = set()

    beat_index = 0
    consecutive_beat_transitions = 0

    while beat_index < len(beat_times) - 1:
        # Determine how long to display the next video(s)
        if consecutive_beat_transitions >= 4:
            # After 4 consecutive beat transitions, allow other patterns
            pattern = random.choice(["single_beat", "two_beat", "half_beat"])
            consecutive_beat_transitions = 0  # Reset counter
        else:
            # 50% of the time, we must transition every beat for at least 4 times in a row
            if consecutive_beat_transitions < 4:
                pattern = "single_beat"
            else:
                # Mix in random patterns
                pattern = random.choices(
                    ["single_beat", "two_beat", "half_beat"], weights=[0.5, 0.25, 0.25]
                )[0]
        
        if pattern == "single_beat":
            # Transition on the current beat
            start_time = beat_times[beat_index]
            end_time = beat_times[beat_index + 1]
            video_path = select_video_file(sorted_video_files, used_videos, video_directory)

            if video_path is None:
                print("All videos have been used. Exiting.")
                break

            try:
                video_clip = create_video_clip(video_path, start_time, end_time)
                clips.append(video_clip)
                consecutive_beat_transitions += 1  # Increment the counter for consecutive beat transitions
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")

            beat_index += 1

        elif pattern == "two_beat" and beat_index < len(beat_times) - 2:
            # Use a single clip for two beats
            start_time = beat_times[beat_index]
            end_time = beat_times[beat_index + 2]
            video_path = select_video_file(sorted_video_files, used_videos, video_directory)

            if video_path is None:
                print("All videos have been used. Exiting.")
                break

            try:
                video_clip = create_video_clip(video_path, start_time, end_time)
                clips.append(video_clip)
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")

            consecutive_beat_transitions = 0  # Reset consecutive beat transitions
            beat_index += 2  # Skip to the next 2-beat interval

        elif pattern == "half_beat" and beat_index < len(beat_times) - 1:
            # Use two clips, each for half a beat
            for _ in range(2):
                start_time = beat_times[beat_index]
                half_beat_duration = (beat_times[beat_index + 1] - beat_times[beat_index]) / 2
                end_time = start_time + half_beat_duration
                video_path = select_video_file(sorted_video_files, used_videos, video_directory)

                if video_path is None:
                    print("All videos have been used. Exiting.")
                    break

                try:
                    video_clip = create_video_clip(video_path, start_time, end_time)
                    clips.append(video_clip)
                except Exception as e:
                    print(f"Error processing video {video_path}: {e}")

                beat_index += 1  # Move forward to the next beat

            consecutive_beat_transitions = 0  # Reset consecutive beat transitions

    if not clips:
        print("No clips were successfully created. Exiting.")
        return

    final_video = concatenate_videoclips(clips).set_audio(audio)
    output_path = os.path.join(video_directory, "stitched_video.mp4")
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    print(f"Stitched video saved as {output_path}")

