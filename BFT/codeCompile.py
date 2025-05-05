import numpy as np
import os
import subprocess
import camera
import yolo11

# Datei-Pfade
script_dir = os.path.dirname(os.path.abspath(__file__))
tensor_path = os.path.join(script_dir, 'Tensor.csv')

# CSV-Datei als NumPy-Array laden
tensor = np.loadtxt(tensor_path, delimiter=",")  # Lade CSV als NumPy-Array


confidence_threshold = 0.1

# Filtere irrelevante Eintraege basierend auf der Konfidenz (Spalte 4)
# filtered_tensor = tensor[tensor[:, 4] > confidence_threshold]

tensor = np.atleast_2d(tensor)
if tensor.shape[1] > 4:
    filtered_tensor = tensor[tensor[:, 4] > confidence_threshold]
else:
    filtered_tensor = np.empty((0, tensor.shape[1]))  # or handle as needed


# Sortiere primär nach y_min und sekundär nach x_min (vertikale Reihenfolge entspricht der Lesereihenfolge)
sorted_tensor = filtered_tensor[np.lexsort((filtered_tensor[:, 0], filtered_tensor[:, 1]))]

# Codes-Tabelle zur Umwandlung der class_id in einen Textnamen
codes = (
    "1", "10", "2", "3", "4", "5", "6", "7", "8", "9",
    "Pausiere", "endif", "endLoop", "if", "lampeAus", "lampeEin",
    "loop", "tasterGedruckt", "tasterNichtGedruckt", "unendlich"
)

# Konvertiere die Eintraege in eine lesbare Struktur (Liste von Dictionaries)
blocks = []
for row in sorted_tensor:
    block = {
        "x_min": row[0],
        "y_min": row[1],
        "x_max": row[2],
        "y_max": row[3],
        "class_id": int(row[5]),  # Sicherstellen, dass class_id eine Ganzzahl ist
        "class_name": codes[int(row[5])]
    }
    blocks.append(block)

# Für die Codegenerierung verwenden wir nur Blokke, die einen Befehl darstellen.
# Die "adjacent info"-Blokke (z. B. "unendlich", "tasterGedruckt", "tasterNichtGedruckt") 
# sollen dabei nicht direkt in den Output gehen.
code_blocks = [b for b in blocks if b["class_name"] not in ("unendlich", "tasterGedruckt", "tasterNichtGedruckt")]

# Sortiere die code_blocks nach y_min (Lesereihenfolge von oben nach unten)
code_blocks.sort(key=lambda b: b["y_min"])

# ----------------------------------------------------------------------------
# Neue Funktion: Bestimme das unmittelbar rechts angrenzende Objekt
# ----------------------------------------------------------------------------
def find_adjacent_info(block, blocks, mode, tolerance=50, vertical_tolerance=50):
    """
    Sucht das Objekt, das unmittelbar rechts von dem gegebenen Block liegt.
    
      - Der horizontale Abstand zwischen block["x_max"] und candidate["x_min"] 
        ist kleiner als 'tolerance' (kleine negative Abstaende werden akzeptiert,
        wenn sich Blokke ueberlappen).
      - Der Unterschied der y_min-Werte liegt innerhalb von 'vertical_tolerance'.
    
    Falls mehrere Kandidaten diese Kriterien erfuellen, wird derjenige mit dem
    kleinsten horizontalen Abstand gewaehlt.
    
    Parameter:
      block: Das Ausgangsobjekt (Dictionary).
      blocks: Liste aller Blokke (die komplette Liste, nicht nur code_blocks).
      mode: "count" oder "taster"
        - "count": 
             * Falls der gefundene Kandidat ein Zahlenblock ist (class_id < 10),
               wird der entsprechende Zahlenwert (den String, wie er in codes steht) 
               zurueckgegeben.
             * Falls der Kandidat den class_name "unendlich" hat (class_id == 19),
               wird "unendlich" zurueckgegeben.
             * Kein Kandidat liefert "1".
        - "taster":
             * Hat der Kandidat den class_name "tasterGedruckt", wird "taster" zurueckgegeben.
             * Bei "tasterNichtGedruckt" wird "not taster" zurueckgegeben.
             * Kein Kandidat liefert "True".
      tolerance: Horizontale Toleranz in Pixeln.
      vertical_tolerance: Vertikale Toleranz in Pixeln.
    
    Returns:
      Den entsprechenden Wert als String.
    """
    best_candidate = None
    best_diff = float('inf')
    for candidate in blocks:
        if candidate is block:
            continue
        diff_x = abs(candidate["x_min"] - block["x_max"])
        diff_y = abs(candidate["y_min"] - block["y_min"])
        if diff_x <= tolerance and diff_y <= vertical_tolerance:
            if diff_x < best_diff:
                best_diff = diff_x
                best_candidate = candidate
    if mode == "count":
        if best_candidate:
            # Falls der Kandidat ein Zahlenblock ist (class_id von 0 bis 9)
            if best_candidate["class_id"] < 10:
                return best_candidate["class_name"]
            elif best_candidate["class_id"] == 19:  # "unendlich"
                return "unendlich"
        return "1"
    elif mode == "taster":
        if best_candidate:
            if best_candidate["class_name"] == "tasterGedruckt":
                return "button.value == 1"
            elif best_candidate["class_name"] == "tasterNichtGedruckt":
                return "button.value == 0"
        return "True"
    else:
        return None

# ----------------------------------------------------------------------------
# Codegenerierung
# ----------------------------------------------------------------------------
output_lines = ["from gpiozero import LED, Button\nfrom time import sleep\n\nled = LED(17)\nbutton = Button(3)\n\n"]
indentation_level = 0

def get_indentation(level):
    return "    " * level

for block in code_blocks:
    code = block["class_name"]
    
    if code == "loop":
        # Suche nach einem direkt rechts angrenzenden Block, um die Wiederholungszahl zu ermitteln.
        loop_count = find_adjacent_info(block, blocks, mode="count", tolerance=50, vertical_tolerance=50)
        if loop_count == "unendlich":
            output_lines.append(f"{get_indentation(indentation_level)}while True:\n")
        else:
            output_lines.append(f"{get_indentation(indentation_level)}for i in range({loop_count}):\n")
        indentation_level += 1
    elif code == "endLoop":
        if indentation_level > 0:
            indentation_level -= 1
    elif code == "if":
        # Suche nach dem unmittelbar rechts angrenzenden Objekt, um die Tasterbedingung zu ermitteln.
        condition = find_adjacent_info(block, blocks, mode="taster", tolerance=50, vertical_tolerance=50)
        output_lines.append(f"{get_indentation(indentation_level)}if {condition}:\n")
        indentation_level += 1
    elif code == "endif":
        if indentation_level > 0:
            indentation_level -= 1
    elif code == "lampeEin":
        output_lines.append(f"{get_indentation(indentation_level)}led.on()\n")
    elif code == "lampeAus":
        output_lines.append(f"{get_indentation(indentation_level)}led.off()\n")
    elif code == "Pausiere":
        paus_count = find_adjacent_info(block, blocks, mode="count", tolerance=50, vertical_tolerance=50)
        # Falls "unendlich" gefunden wird, verwenden wir stattdessen 1
        if paus_count == "unendlich":
            paus_count = "1"
        output_lines.append(f"{get_indentation(indentation_level)}sleep({paus_count})\n")

# Schreibe die generierten Python-Befehle in eine neue Datei
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(script_dir, "final.py")
with open(output_file_path, "w") as file:
    file.writelines(output_lines)

print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")
subprocess.run(["python", "final.py"])
