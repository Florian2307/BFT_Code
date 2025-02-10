import torch
from ultralytics import YOLO
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'best.pt')
model = YOLO(model_path)
image_path = os.path.join(script_dir, 'Screenshot 2025-02-10 110522.png')
results = model(image_path, save=True)
output_tensor = results[0].boxes.data  # Rohdaten des ersten Bildes (Tensor)

output_file_path = os.path.join(script_dir, 'Tensor.csv')

with open(output_file_path, "w") as file:
    for row in output_tensor.tolist():  # Konvertiere den Tensor in eine Python-Liste
        formatted_row = [f"{val:.6f}" for val in row]  # Formatiere Zahlen mit 6 Dezimalstellen
        file.write(",".join(formatted_row) + "\n")  # CSV-Format mit Komma

print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")