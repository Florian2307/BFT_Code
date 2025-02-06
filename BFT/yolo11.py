import torch
from ultralytics import YOLO
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'best.pt')
model = YOLO(model_path)
image_path = os.path.join(script_dir, 'Screenshot 2025-02-06 155203.png')
results =model(image_path,save=True)
output_tensor = results[0].boxes.data  # Rohdaten des ersten Bildes (Tensor)
print(output_tensor)

output_file_path = "Tensor.csv"

with open(output_file_path, "w") as file:
    for row in output_tensor.tolist():  # Konvertiere den Tensor in eine Python-Liste
        file.write(",".join(map(str, row)) + "\n")  # CSV-Format mit Komma

print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")
