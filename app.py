from flask import Flask, render_template, request, jsonify
import os
import sys
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPlainTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import pyttsx3
import pygame

# --- Flask App Setup ---
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 * 1024  # 20 GB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Voice and Sound Setup ---
pygame.mixer.init()

def play_notification_sound():
    try:
        pygame.mixer.music.load("notification.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("Notification sound error:", e)

voice_engine = pyttsx3.init()

def speak(text):
    play_notification_sound()
    voice_engine.say(text)
    voice_engine.runAndWait()

# --- Signal Communicator ---
class Communicator(QObject):
    new_message = pyqtSignal(str)

comm = Communicator()

# --- GUI Window ---
class UploadWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📁 File Uploader - Shubham Sharma")
        self.setGeometry(200, 200, 800, 500)

        self.layout = QVBoxLayout()
        self.welcome_label = QLabel(f"🚀 File Sender App started! Uploads will be saved to: {UPLOAD_FOLDER}")
        self.welcome_label.setWordWrap(True)
        self.layout.addWidget(self.welcome_label)

        self.log_box = QPlainTextEdit()
        self.log_box.setAccessibleName("Upload Log Box")
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        self.setLayout(self.layout)
        self.counter = 1
        comm.new_message.connect(self.append_message)

    def append_message(self, msg):
        full_msg = f"{self.counter}. {msg}"
        self.log_box.appendPlainText(full_msg)
        self.log_box.moveCursor(self.log_box.textCursor().End)
        self.log_box.setFocus()
        speak(msg)
        self.counter += 1

# --- Qt Application Initialization ---
qt_app = QApplication(sys.argv)
window = UploadWindow()

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    username = request.form.get('username')
    uploaded_file = request.files.get('file')

    if not username:
        return jsonify({'status': 'error', 'message': 'Full name is required.'}), 400
    if not uploaded_file or uploaded_file.filename.strip() == '':
        return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400

    safe_username = secure_filename(username)
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], safe_username)
    os.makedirs(user_folder, exist_ok=True)

    original_filename = secure_filename(uploaded_file.filename)
    filename = original_filename
    name, ext = os.path.splitext(filename)
    file_counter = 2
    while os.path.exists(os.path.join(user_folder, filename)):
        filename = f"{name} ({file_counter}){ext}"
        file_counter += 1

    file_path = os.path.join(user_folder, filename)

    try:
        uploaded_file.save(file_path)
        upload_time = datetime.now().strftime('%I:%M %p')
        msg = f"One file received from {username} at {upload_time}"
        comm.new_message.emit(msg)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to save file: {str(e)}'}), 500

    return jsonify({'status': 'success', 'message': f'File \"{filename}\" uploaded successfully.'})

# --- Run App + GUI ---
def run_flask():
    app.run(debug=False, use_reloader=False)

def start_gui():
    window.show()
    window.log_box.setFocus()
    qt_app.exec_()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    start_gui()