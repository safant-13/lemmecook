import os
import sounddevice as sd
import soundfile as sf
import numpy as np
import google.generativeai as genai
import pyttsx3  # <--- Import pyttsx3
from dotenv import load_dotenv
import time

# --- Configuration ---
load_dotenv()
# We no longer need the ElevenLabs API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# --- VAD Configuration ---
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024

# --- State Management ---
is_speaking = False

# --- Initialize Clients ---
# Remove ElevenLabs client
genai.configure(api_key=gemini_api_key)

# --- Initialize pyttsx3 Engine ---
tts_engine = pyttsx3.init()

# --- Function to speak text using pyttsx3 (The major change) ---
def speak(text):
    """Generates and plays audio locally, managing the 'is_speaking' state."""
    global is_speaking
    is_speaking = True
    print("🔊 The boss is speaking...")
    try:
        # Use the local TTS engine
        tts_engine.say(text)
        tts_engine.runAndWait() # This call blocks until speaking is finished
    except Exception as e:
        print(f"An error occurred with pyttsx3: {e}")
    finally:
        is_speaking = False
        print("\n----- Ready for your next command -----")


def main():
    """Main function to run the live conversation loop."""
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction="You are a sarcastic, old and angry Italian mob boss running a kitchen in New York. Keep your responses concise and to the point, like a real conversation. You have a short temper."
    )
    chat = model.start_chat()
    print("🤌 The boss is ready to talk. (Press Ctrl+C to exit)")

    while True:
        recorded_frames = []
        is_recording = False
        silent_chunks = 0
        max_silent_chunks = int(SILENCE_DURATION * SAMPLE_RATE / CHUNK_SIZE)

        print("🎙️ Listening...")
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=CHUNK_SIZE, dtype='float32') as stream:
            while True:
                if is_speaking:
                    time.sleep(0.1)
                    continue

                audio_chunk, overflowed = stream.read(CHUNK_SIZE)
                volume = np.linalg.norm(audio_chunk)

                if volume > SILENCE_THRESHOLD:
                    if not is_recording:
                        print("... I hear you ...")
                        is_recording = True
                    recorded_frames.append(audio_chunk)
                    silent_chunks = 0
                elif is_recording:
                    silent_chunks += 1
                    recorded_frames.append(audio_chunk)
                    if silent_chunks > max_silent_chunks:
                        print("... You finished talking.")
                        break
        
        if recorded_frames:
            audio_data = np.concatenate(recorded_frames, axis=0)
            audio_filename = "input.ogg"
            sf.write(audio_filename, audio_data, SAMPLE_RATE)

            print("🤌 The boss is thinking...")
            try:
                audio_file = genai.upload_file(path=audio_filename)
                response = chat.send_message([
                    "Listen to this audio and give me a short, sarcastic reply:",
                    audio_file
                ])
                genai.delete_file(audio_file.name)
                os.remove(audio_filename)

                print(f"Grandma says: {response.text}")
                speak(response.text)

            except Exception as e:
                print(f"An error occurred with Gemini: {e}")


if __name__ == "__main__":
    main()