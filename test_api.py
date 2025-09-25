import os
import sounddevice as sd
from scipy.io.wavfile import write
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()

# --- Get API keys from environment variables ---
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# --- Initialize ElevenLabs client ---
client = ElevenLabs(api_key=elevenlabs_api_key)

# --- Function to speak text using ElevenLabs ---
def speak(text):
    """Generates audio from text using a specific voice and plays it."""
    try:
        audio = client.generate(
            text=text,
            voice="Antonio",  # You can use the voice name directly
            model="eleven_multilingual_v2"
        )
        play(audio)
    except Exception as e:
        print(f"An error occurred with ElevenLabs: {e}")

# --- Step 1: Record audio ---
duration = 5
sample_rate = 44100
print("🎙️ Speak now... (5 seconds)")
audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
sd.wait()
write("input.wav", sample_rate, audio_data)
print("✅ Recorded audio saved as input.wav")

# --- Step 2: Configure Gemini ---
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction="You are a sarcastic, old and angry Italian mob boss running a kitchen in New York. Respond with attitude and humor."
)

# --- Step 3: Send audio to Gemini ---
print("🤌 The boss is listening...")
try:
    # Upload the local file to the Gemini API
    audio_file = genai.upload_file(path="input.wav")

    response = model.generate_content([
        "Listen to this audio and reply sarcastically:",
        audio_file
    ])

    # Clean up the uploaded file
    genai.delete_file(audio_file.name)

    # --- Step 4: Output & speak ---
    print("Grandma says:", response.text)
    speak(response.text)

except Exception as e:
    print(f"An error occurred with Gemini: {e}")

finally:
    # Clean up the local audio file
    if os.path.exists("input.wav"):
        os.remove("input.wav")
        print("✅ Cleaned up input.wav")