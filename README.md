# 🎥 Video Audio Fixer (AAC Converter)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=for-the-badge&logo=flask)
![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Powered-green?style=for-the-badge&logo=ffmpeg)

> A lightweight, robust web application that converts video audio tracks to Universal AAC format while preserving original video quality.

---

## 🚀 Overview

Many modern TVs, web players, and older devices struggle to play specific audio formats (like DTS, EAC3, or TrueHD) even if they can handle the video perfectly.

**Video Audio Fixer** solves this by using **FFmpeg** to transcode *only* the audio stream to stereo AAC (the most compatible format) while copying the video stream byte-for-byte.

**The Result:** A file that plays everywhere, processed in seconds rather than hours, with zero video quality loss.

---

## ✨ Key Features

* **⚡ Zero-Loss Video Processing:** Uses `ffmpeg -c:v copy` to pass video data through without re-encoding.
* **🔊 Universal Audio:** Converts complex audio codecs to standard AAC (192k Stereo).
* **🛡️ Secure & Robust:**
    * UUID-based filenames to prevent collisions.
    * Strict file type validation (`.mp4`, `.mkv`, `.mov`, `.avi`).
    * Automatic background cleanup (files are deleted 5 minutes after processing).
* **🎨 Modern UI:**
    * Clean, responsive interface built with **Tailwind CSS**.
    * Drag-and-drop file upload zone.
    * **Real-time Feedback:** Download Token pattern prevents the "frozen screen" issue during large file processing.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Werkzeug.
* **Media Engine:** FFmpeg.
* **Frontend:** HTML5, JavaScript (Cookie Polling), Tailwind CSS (CDN).
* **Concurrency:** Python `threading` for non-blocking file cleanup.

---

## ⚙️ Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** and **FFmpeg** installed on your system.

* **MacOS:** `brew install ffmpeg`
* **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
* **Windows:** [Download FFmpeg](https://ffmpeg.org/download.html) and add the `bin` folder to your System PATH.

### 2. Clone & Setup

```bash
# Clone the repository
git clone [https://github.com/yourusername/video-audio-fixer.git](https://github.com/yourusername/video-audio-fixer.git)
cd video-audio-fixer

# Create a virtual environment (Recommended)
python -m venv venv

# Activate Virtual Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install flask