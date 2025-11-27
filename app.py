import os
import uuid
import time
import shutil
import threading
import logging
import subprocess
from pathlib import Path
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, make_response
from werkzeug.utils import secure_filename

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp4", "mkv", "mov", "avi", "webm", "flv"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2 GB Limit

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-key-change-in-prod")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# --- Helpers ---

def check_ffmpeg():
    """Checks if FFmpeg is installed and accessible."""
    if not shutil.which("ffmpeg"):
        logger.critical("FFmpeg is not installed or not in PATH. Application cannot function.")
        raise RuntimeError("FFmpeg not found. Please install FFmpeg.")

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def delayed_cleanup(file_paths: list[Path], delay: int = 60):
    """
    Deletes files after a delay in a background thread.
    This ensures the file isn't deleted while Flask is still streaming it to the user.
    """
    def _delete():
        time.sleep(delay)
        for path in file_paths:
            try:
                if path.exists():
                    path.unlink()
                    logger.info(f"Cleaned up file: {path.name}")
            except Exception as e:
                logger.error(f"Error cleaning up {path.name}: {e}")
    
    # Start the background thread
    thread = threading.Thread(target=_delete)
    thread.daemon = True
    thread.start()

# --- Routes ---

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", max_size=MAX_CONTENT_LENGTH)

@app.route("/convert", methods=["POST"])
def convert():
    # 1. Input Validation
    if "file" not in request.files:
        flash("No file part in request.")
        return redirect(url_for("index"))

    file = request.files["file"]
    
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        return redirect(url_for("index"))

    # 2. Secure Save
    original_filename = secure_filename(file.filename)
    unique_id = uuid.uuid4().hex
    input_filename = f"{unique_id}_{original_filename}"
    input_path = UPLOAD_DIR / input_filename
    
    output_filename = f"converted_{unique_id}.mp4"
    output_path = UPLOAD_DIR / output_filename

    try:
        file.save(input_path)
        logger.info(f"File uploaded: {input_path}")
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        flash("Failed to save uploaded file.")
        return redirect(url_for("index"))

    # 3. FFmpeg Command
    # -c:v copy : Copies video stream exactly (no quality loss, very fast)
    # -c:a aac  : Converts audio to AAC
    # -movflags +faststart : Optimizes MP4 for web streaming
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",               
        "-i", str(input_path),
        "-c:v", "copy",     
        "-c:a", "aac",      
        "-b:a", "192k",     
        "-movflags", "+faststart",
        str(output_path)
    ]

    try:
        logger.info("Starting FFmpeg conversion...")
        subprocess.run(
            ffmpeg_cmd, 
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=3600 # 1 hour timeout for large files
        )
        logger.info("Conversion successful.")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr}")
        flash("Conversion failed. The file might be corrupt.")
        delayed_cleanup([input_path]) 
        return redirect(url_for("index"))
    
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timed out.")
        flash("File is too large or conversion took too long.")
        delayed_cleanup([input_path, output_path])
        return redirect(url_for("index"))

    # 4. Schedule Cleanup (Wait 5 mins for download to finish)
    delayed_cleanup([input_path, output_path], delay=300)

    # 5. Send File & Set Cookie for Frontend Spinner
    response = make_response(send_file(
        output_path,
        as_attachment=True,
        download_name=f"{Path(original_filename).stem}_aac.mp4",
        mimetype="video/mp4"
    ))

    # Retrieve the token sent by the frontend
    download_token = request.form.get("download_token")
    if download_token:
        # Set a cookie with the same token. The frontend watches for this cookie.
        response.set_cookie("download_token", download_token, max_age=60)

    return response

if __name__ == "__main__":
    check_ffmpeg()
    app.run(host="0.0.0.0", port=1800, debug=True)