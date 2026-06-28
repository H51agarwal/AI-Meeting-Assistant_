import os
import uuid
import whisper
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

whisper_model = whisper.load_model("base")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ALLOWED_EXTENSIONS = {"mp4", "mkv", "mp3", "wav", "m4a"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, audio_path):
    """Extract audio from video using moviepy."""
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, logger=None)
    clip.close()

def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def process_with_groq(transcript):
    prompt = f"""You are a meeting assistant. Given this meeting transcript, provide:
    1. SUMMARY: A short paragraph summarizing the meeting.
    2. ACTION ITEMS: A checklist like "- Rahul: design UI by Friday"

    Transcript:
    {transcript}"""

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use mp4, mkv, mp3, wav, m4a"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_name}.{ext}")
    file.save(input_path)

    if ext in {"mp4", "mkv"}:
        audio_path = os.path.join(UPLOAD_FOLDER, f"{unique_name}.mp3")
        try:
            extract_audio(input_path, audio_path)
        except Exception as e:
            return jsonify({"error": f"Audio extraction failed: {str(e)}"}), 500
    else:
        audio_path = input_path

    try:
        transcript = transcribe_audio(audio_path)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    
    try:
        result = process_with_groq(transcript)
    except Exception as e:
        return jsonify({"error": f"LLM processing failed: {str(e)}"}), 500

    os.remove(input_path)
    if audio_path != input_path:
        os.remove(audio_path)

    return jsonify({"transcript": transcript, "result": result})

if __name__ == "__main__":
    app.run(debug=True, port=5000)