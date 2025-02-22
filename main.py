import sounddevice as sd
import numpy as np
import wave
import openai
import requests
import json
import os
import time
from scipy.io.wavfile import write
from bs4 import BeautifulSoup
import re
import ffmpeg
import glob

# OpenAI API Key
OPENAI_API_KEY = ""

# Recording parameters
SAMPLE_RATE = 44100 # Sampling rate
DURATION = 5  # Recording duration (seconds)
AUDIO_FILENAME = "recorded_audio.wav"


# Record audio
def record_audio():
    print("Recording...")
    recording = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    write(AUDIO_FILENAME, SAMPLE_RATE, recording)
    print(f"Recording saved as {AUDIO_FILENAME}")


# Transcribe audio using OpenAI Whisper API
def transcribe_audio(filename):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    files = {
        "file": (filename, open(filename, "rb"), "audio/wav")
    }
    data = {
        "model": "whisper-1"
    }
    response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
    result = response.json()
    text = result.get("text", "")
    print("Transcribed Text:", text)
    return text


# Translate text to ASL Gloss using GPT-4o
def translate_to_asl_gloss(text):
    prompt = f"""
    Here are some examples of translations from English text to ASL gloss:
    Examples:
    Apples ==> APPLE
    you  ==> IX-2P
    your  ==> IX-2P
    Love ==> LIKE
    My ==> IX-1P
    Thanks ==> THANK-YOU
    am ==> 
    and ==> 
    be ==>
    of ==>
    video ==> MOVIE
    image ==> PICTURE
    conversations ==> TALK
    type of ==> TYPE
    ? ==> QUESTION
    Watch ==> SEE

    Translate the following English text to ASL Gloss and surround it with tags <gloss> and </gloss>:
    {text}
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    result = response.json()
    gloss_text = result["choices"][0]["message"]["content"]

    gloss_list = extract_gloss_list(gloss_text)
    print("Extracted ASL Gloss:", gloss_list)
    return gloss_list


# Extract ASL Gloss words from GPT response
def extract_gloss_list(gloss_text):
    gloss_words = []
    start_tag = "<gloss>"
    end_tag = "</gloss>"

    if start_tag in gloss_text and end_tag in gloss_text:
        gloss_text = gloss_text.split(start_tag)[1].split(end_tag)[0]
        gloss_words = gloss_text.split()
    return gloss_words


# Retrieve ASL Gloss video URLs from SignBank
def get_gloss_video_urls(gloss_list):
    video_urls = []

    for gloss in gloss_list:
        search_url = f"https://dai.cs.rutgers.edu/dai/s/maingloss?sign_tag=0&key_word={gloss}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first "Play Sign Video" button's link
        for button in soup.find_all("input", {"value": "Play Sign Video"}):
            onclick_attr = button.get("onclick", "")
            # print("Extracted onclick attribute:", onclick_attr)

             # Extract URL from return popup('...') using regex
            match = re.search(r"popup\('([^']+)'\)", onclick_attr)
            if match:
                video_url = f"https://dai.cs.rutgers.edu/dai/s/{match.group(1)}"
                video_urls.append(video_url)
                break   # Take only the first matching video

    print("Retrieved Video URLs:", video_urls)
    return video_urls

# Delete old videos
def delete_old_videos():
    """ Delete all .mp4 files that start with a number and an underscore """
    video_files = glob.glob("[0-9]_*.mp4") 
    for file in video_files:
        try:
            os.remove(file)
            print(f"Deleted old video: {file}")
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

# Download videos
def download_videos(video_urls, gloss_list):
    """ Delete old videos before downloading new ones """
    delete_old_videos()  

    downloaded_videos = []
    for i, (url, gloss) in enumerate(zip(video_urls, gloss_list)):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        video_tag = soup.find("video")
        if video_tag:
            source_tag = video_tag.find("source")
            if source_tag:
                video_link = source_tag["src"]
                video_filename = f"{i}_{gloss}.mp4"  # Name format: index_gloss.mp4

                with open(video_filename, "wb") as f:
                    f.write(requests.get(video_link).content)

                downloaded_videos.append(video_filename)
                print(f"Downloaded video: {video_filename}")

    return downloaded_videos


# def merge_videos(video_files, output_filename="final_asl_video.mp4"):
#     input_streams = [ffmpeg.input(video) for video in video_files]
#     output = ffmpeg.concat(*input_streams, v=1, a=1).output(output_filename)
#     output.run()
#     print(f"Final ASL video saved as {output_filename}")


def get_video_duration(video_file):
    probe = ffmpeg.probe(video_file)
    duration = float(probe["format"]["duration"])
    return duration

def get_video_frame_count(video_file):
    probe = ffmpeg.probe(video_file)
    return int(probe["streams"][0]["nb_frames"]) 

def sanitize_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text) 
    return text.strip() 


def normalize_video(input_file, output_file, gloss_text, resolution="1280x720", fps=30):
    """ Standardize video format, ensure duration is between 1.5s ~ 3s, and add ASL Gloss text """

    gloss_text = sanitize_text(gloss_text)

    try:
        duration = get_video_duration(input_file)
        frame_count = get_video_frame_count(input_file)
    except Exception:
        print(f"Error reading video {input_file}. Assuming duration = 0.")
        duration, frame_count = 0, 0  # Handle corrupted video

    # Select font (adapt for different systems)
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS
    # font_path = "C:/Windows/Fonts/arial.ttf"  # Windows
    # font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux

    # Define text box
    text_filter = (
        f"drawtext=text='{gloss_text}':fontfile={font_path}:"
        "fontcolor=white:fontsize=40:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10"
    )

    if duration == 0 or frame_count <= 1:
        # Use loop to repeat a single frame for 1.5 seconds
        ffmpeg.input(input_file, stream_loop=-1, t=1.5).output(
            output_file, vf=f"scale={resolution},fps={fps},{text_filter}", r=fps, vcodec="libx264", acodec="aac"
        ).run(overwrite_output=True)
        print(f"Repeated static frame for 1.5s: {input_file}")

    elif duration < 1.5:
        # Short video (<1.5s): Slow down playback to extend to 1.5 seconds
        slow_factor = 1.5 / duration
        ffmpeg.input(input_file).output(
            output_file, vf=f"scale={resolution},setpts={slow_factor}*PTS,{text_filter}", r=fps, vcodec="libx264",
            acodec="aac"
        ).run(overwrite_output=True)
        print(f"Extended short video {input_file} to 1.5 seconds.")

    elif duration > 3:
        # Long video (>3s): Speed up playback to fit within 3 seconds
        speed_factor = duration / 3
        ffmpeg.input(input_file).output(
            output_file, vf=f"scale={resolution},setpts={1 / speed_factor}*PTS,{text_filter}", r=fps, vcodec="libx264",
            acodec="aac"
        ).run(overwrite_output=True)
        print(f"Sped up long video {input_file} to 3 seconds.")

    else:
        # Normal duration video, directly convert format
        ffmpeg.input(input_file).output(
            output_file, vf=f"scale={resolution},{text_filter}", r=fps, vcodec="libx264", acodec="aac"
        ).run(overwrite_output=True)

# Merge videos
def merge_videos(video_files, gloss_list, output_filename="final_asl_video.mp4"):
    """ Normalize video formats, add ASL Gloss text, and merge """
    temp_files = []

    for i, (video, gloss) in enumerate(zip(video_files, gloss_list)):
        temp_file = f"temp_{i}.mp4"
        normalize_video(video, temp_file, gloss)
        temp_files.append(temp_file)

    with open("file_list.txt", "w") as f:
        for video in temp_files:
            f.write(f"file '{video}'\n")

    ffmpeg.input("file_list.txt", format="concat", safe=0).output(
        output_filename, vcodec="libx264", acodec="aac"
    ).run(overwrite_output=True)

    for file in temp_files:
        os.remove(file)

    print(f"Final ASL video saved as {output_filename}")


# Play merged video
def play_video(video_filename):
    os.system(f"start {video_filename}" if os.name == "nt" else f"open {video_filename}")

def main():
    record_audio()
    text = transcribe_audio(AUDIO_FILENAME)
    if not text:
        print("No text transcribed.")
        return

    gloss_list = translate_to_asl_gloss(text)  
    if not gloss_list:
        print("No ASL gloss extracted.")
        return

    video_urls = get_gloss_video_urls(gloss_list) 
    if not video_urls:
        print("No videos found for ASL gloss.")
        return

    video_files = download_videos(video_urls, gloss_list) 
    if not video_files:
        print("No videos downloaded.")
        return

    merge_videos(video_files, gloss_list) 
    play_video("final_asl_video.mp4") 


if __name__ == "__main__":
    main()
