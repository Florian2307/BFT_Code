#!/usr/bin/env python3

from gpiozero import Button
from multiprocessing import Process
import time
import os
import psutil

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_path = "./BFT/codeCompile.py"
os.chdir(dir_path)

button = Button(2)
current_process = None

def log(message):
    with open("autostart_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

log(f"Current working directory: {os.getcwd()}")

def run_compile():
    try:
        os.system(f"python3 {file_path}")
    except Exception as e:
        log(f"Fehler beim Ausführen von {file_path}: {e}\n")

def terminate_subprocess():
    script_name = "/home/aicam/Desktop/BFT/code/BFT/final.py"
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in proc.info['cmdline']:
                log(f"Beende Subprozess: {proc.info['cmdline']}")
                proc.kill()
                time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def toggle_process():
    global current_process
    if current_process and current_process.is_alive():
        log("Stoppe alten Prozess...")
        terminate_subprocess()
        current_process.terminate()
        current_process.join()
    log("Starte neuen Prozess...")
    current_process = Process(target=run_compile)
    current_process.start()


button.when_pressed = toggle_process

log("autostart.py mit multiprocessing gestartet...")
while True:
    time.sleep(1)
