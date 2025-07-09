from gpiozero import Button
from multiprocessing import Process
import time
import os
import psutil

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_path = "./BFT/codeCompile.py"
os.chdir(dir_path)

button = Button(3)
current_process = None

def log(message):
    with open("autostart_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

print(f"Current working directory: {os.getcwd()}")

def run_compile():
    try:
        os.system(f"python3 {file_path}")
    except Exception as e:
        print(f"Fehler beim Ausführen von {file_path}: {e}\n")

def terminate_subprocess():
    script_name = "/home/aicam/Desktop/BFT/code/BFT/final.py"
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in proc.info['cmdline']:
                print(f"Beende Subprozess: {proc.info['cmdline']}")
                proc.kill()
                time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def toggle_process():
    global current_process
    if current_process and current_process.is_alive():
        print("Stoppe alten Prozess...")
        terminate_subprocess()
        current_process.terminate()
        current_process.join()
    print("Starte neuen Prozess...")
    current_process = Process(target=run_compile)
    current_process.start()

def button_pressed():
    if button.is_pressed:
        print("Button is pressed, starting process...")
        toggle_process()


print("autostart.py mit multiprocessing gestartet...")
while True:
    button_pressed()
    time.sleep(0.1)  # Polling delay to avoid high CPU usage
