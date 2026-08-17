import os
import sys
import time
import queue
import tempfile
import threading
import subprocess
import sounddevice as sd
import soundfile as sf
from pynput import keyboard
import mlx_whisper

SAMPLE_RATE = 16000
CHANNELS = 1
MODEL_PATH = "mlx-community/whisper-large-v3-turbo"

DOUBLE_CLICK_INTERVAL = 0.4
last_ctrl_press_time = 0

is_recording = False
audio_queue = queue.Queue()
record_thread = None
temp_audio_path = None

def play_sound(sound_name):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.Popen(["afplay", sound_path])

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[Audio Status] {status}", file=sys.stderr)
    if is_recording:
        audio_queue.put(indata.copy())

def record_audio(filename):
    global is_recording
    with sf.SoundFile(filename, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS) as file:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
            while is_recording:
                while not audio_queue.empty():
                    file.write(audio_queue.get())
                time.sleep(0.05)
            while not audio_queue.empty():
                file.write(audio_queue.get())

def paste_text(text):
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, close_fds=True)
    process.communicate(input=text.encode('utf-8'))
    
    time.sleep(0.08)
    applescript = '''
    tell application "System Events"
        key code 9 using command down
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
    play_sound("Pop")

def process_and_transcribe(audio_path):
    print("\n⏳ Расшифровываю...")
    try:
        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=MODEL_PATH,
            language="ru",
            temperature=0.0
        )
        text = result.get("text", "").strip()
        if text:
            print(f"✅ Готово: {text}")
            paste_text(text)
        else:
            print("⚠️ Голос не обнаружен.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

def start_recording():
    global is_recording, record_thread, temp_audio_path
    is_recording = True
    temp_fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_fd)
    
    while not audio_queue.empty():
        audio_queue.get()
        
    play_sound("Tink")
    print("\n🎙️ [ЗАПИСЬ ПОШЛА...] Нажмите Control один раз для остановки.")
    record_thread = threading.Thread(target=record_audio, args=(temp_audio_path,))
    record_thread.start()

def stop_recording():
    global is_recording, record_thread, temp_audio_path
    is_recording = False
    if record_thread:
        record_thread.join()
    print("⏹️ Запись остановлена. Обработка...")
    threading.Thread(target=process_and_transcribe, args=(temp_audio_path,)).start()

def on_press(key):
    global last_ctrl_press_time, is_recording
    
    if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        current_time = time.time()
        
        if is_recording:
            stop_recording()
            last_ctrl_press_time = 0
        else:
            if current_time - last_ctrl_press_time <= DOUBLE_CLICK_INTERVAL:
                last_ctrl_press_time = 0
                start_recording()
            else:
                last_ctrl_press_time = current_time

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Фоновый голосовой ввод запущен!")
    print("👉 Старт записи: Быстро 2 раза нажать [ Control ]")
    print("👉 Стоп записи:  1 раз нажать [ Control ]")
    print("=" * 60)
    
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
