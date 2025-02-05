import numpy as np
import timeit
import os 

script_dir = os.path.dirname(os.path.abspath(__file__))
tensor_path = os.path.join(script_dir, 'Tensor.csv')
codes_path = os.path.join(script_dir, 'codes.csv')

# CSV-Datei als NumPy-Array laden
tensor = np.array([
   [50,  30, 100, 80, 0.9, 2],    # "if"
   [110, 35, 130, 55, 0.95, 4],   # "tasterGedrückt" 
   [150, 35, 170, 55, 0.9, 6],    # "lampeEin"
   [50, 100, 100, 150, 0.8, 3],   # "endIf"
])
# Konfidenzschwelle
confidence_threshold = 0.5

# Filtere irrelevante Einträge basierend auf der Konfidenz (Spalte 4)
filtered_tensor = tensor[tensor[:, 4] > confidence_threshold]

# Sortiere nach x_min (Spalte 0)
sorted_tensor = filtered_tensor[np.argsort(filtered_tensor[:, 0])]

# Konvertiere die Einträge in eine lesbare Struktur (Liste von Dictionaries)
blocks = []
for row in sorted_tensor:
    block = {
        "x_min": row[0],
        "y_min": row[1],
        "x_max": row[2],
        "y_max": row[3],
        "class_id": int(row[5])  
    }
    blocks.append(block)
 
codes = (
    "loop", "endLoop", "if", "endIf", "tasterGedrückt", "tasterNichtGedrückt", "lampeEin","lampeAus","Pausiere", "1", "2", "3",
    "4", "5", "6", "7", "8", "9", "10", "unendlich"
)
  
# Generiere Python-Code basierend auf den Blocks
output_lines = ["import time \nimport RPi .GPIO as GPIO\n\n"]
indentation_level = 0
 
def get_indentation(level):
    return "    " * level
 

def find_count(block, blocks, tolerance=50, toleranceY=-50):
    for candidate in blocks:
        if 9 <= candidate["class_id"] <= 19:
            y_diff = candidate["y_min"] - block["y_min"]
            if (abs(candidate["x_min"] - block["x_max"]) <= tolerance and
                (y_diff <= tolerance and y_diff >= toleranceY)):
                
                return "unendlich" if candidate["class_id"] == 21 else str(candidate["class_id"] - 10)
                
    return "1"


def findTaster(block, blocks, tolerance=50, toleranceY=-50):
    for candidate in blocks:
        if candidate["class_id"] in [4, 5]:
            y_diff = candidate["y_min"] - block["y_min"]
            if (abs(candidate["x_min"] - block["x_max"]) <= tolerance and
                (y_diff <= tolerance and y_diff >= toleranceY)):
                
                if candidate["class_id"] == 4:
                    return "taster"
                
                if candidate["class_id"] == 5:
                    return "not taster"
                
    return "True"


 
for block in blocks:
    class_id = block["class_id"]
    if class_id <= len(codes):  # Sicherstellen, dass der Index gültig ist
        code = codes[class_id]
        if code == "loop":
            loop_count = find_count(block, blocks)
            if loop_count == "unendlich":
                output_lines.append(f"{get_indentation(indentation_level)}while True:\n")
            else:   
                output_lines.append(f"{get_indentation(indentation_level)}for i in range({loop_count}):\n")
            indentation_level += 1  # Einrückung erhöhen
        elif code == "endLoop":
            if indentation_level > 0:
                indentation_level -= 1  # Einrückung reduzieren
        elif code == 'if':
            bedinnung = findTaster(block, blocks)
            output_lines.append(f"{get_indentation(indentation_level)}if({bedinnung}):\n")
            indentation_level += 1
        elif code == 'endIf':
            if indentation_level > 0:
                indentation_level -= 1
        elif code == "lampeEin":
            output_lines.append(f"{get_indentation(indentation_level)}lampe.turn_on()\n")
        elif code == "lampeAus":
            output_lines.append(f"{get_indentation(indentation_level)}lampe.turn_off()\n")
        elif code == "Pausiere":
            paus_count = find_count(block, blocks)
            if paus_count == "unendlich":
                paus_count = 1
            output_lines.append(f"{get_indentation(indentation_level)}time.sleep({paus_count})\n")
    else:
        print(f'invalid class id ${class_id}')


# Schreibe die generierten Python-Befehle in eine neue Datei
output_file_path = "output_dynamic_loops.py"
with open(output_file_path, "w") as file:
    file.writelines(output_lines)
 
print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")