from ultralytics import YOLO
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'code.png')

    create_tensor(image_path, script_dir)


def create_tensor(image_path, dest_dir):
    model_path = os.path.join(dest_dir, 'best.pt')
    model = YOLO(model_path)
    results = model(image_path, save=True)
    output_tensor = results[0].boxes.data
    output_file_path = os.path.join(dest_dir, 'Tensor.csv')

    with open(output_file_path, "w") as file:
        for row in output_tensor.tolist():  # Konvertiere den Tensor in eine Python-Liste
            formatted_row = [f"{val:.6f}" for val in row]  # Formatiere Zahlen mit 6 Dezimalstellen
            file.write(",".join(formatted_row) + "\n")  # CSV-Format mit Komma

    print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")
    return output_file_path

if __name__ == "__main__":
    main()