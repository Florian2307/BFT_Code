import torch
import timeit
import sys
 
# Eingabe-Tensor mit Daten
tensor = torch.tensor([
    [100.000, 200.000, 300.000, 400.000, 0.95, 0],  # loop
    [110.000, 210.000, 310.000, 410.000, 0.95, 21],  # unendlich
    [200.000, 300.000, 400.000, 500.000, 0.95, 7],   # Lampe1
    [300.000, 400.000, 500.000, 600.000, 0.95, 1]    # endLoop
])
 
# Konfidenzschwelle
confidence_threshold = 0.5
 
# Filtere irrelevante Einträge basierend auf der Konfidenz (Spalte 4)
filtered_tensor = tensor[tensor[:, 4] > confidence_threshold]
 
# Sortiere nach x_min (Spalte 0)
sorted_tensor = filtered_tensor[filtered_tensor[:, 0].argsort()]
 
# Konvertiere die Einträge in eine lesbare Struktur (Liste von Dictionaries)
blocks = []
for row in sorted_tensor:
    block = {
        "x_min": row[0].item(),
        "y_min": row[1].item(),
        "x_max": row[2].item(),
        "y_max": row[3].item(),
        "class_id": int(row[5].item())
    }
    blocks.append(block)
 
# Definition der Codes für die Klassen
 
 
codes = (
    "loop", "endLoop", "if", "endIf", "taster1Gedrückt", "taster2Gedrückt",
    "schalter1Umgelegt", "lampe1", "lampe2", "lampe3", "Pausiere", "1", "2", "3",
    "4", "5", "6", "7", "8", "9", "10", "unendlich"
)
 
print(codes)
keywoards = [
 
 
]
 
# Generiere Python-Code basierend auf den Blocks
output_lines = ["# Dieses File wurde automatisch generiert\n\n"]
indentation_level = 0
 
def get_indentation(level):
    """Gibt die Einrückung basierend auf dem aktuellen Level zurück."""
    return "    " * level
 
def find_loop_count(block, blocks, tolerance=50):
    """Sucht die Zahl oder 'unendlich' rechts neben einer Schleife."""
    for candidate in blocks:
        if (
            candidate["x_min"] > block["x_max"]  # Rechts von der Schleife
            and abs(candidate["y_min"] - block["y_min"]) <= tolerance  # Gleiche Höhe
            and 11 <= candidate["class_id"] <= 21  # Zahl oder 'unendlich'
        ):
            return codes[candidate["class_id"]]
    return "1"  # Standardwert, wenn keine Zahl gefunden wird
 
for block in blocks:
    class_id = block["class_id"]
    if class_id < len(codes):  # Sicherstellen, dass der Index gültig ist
        code = codes[class_id]
        if code == "loop":
            loop_count = find_loop_count(block, blocks)
            if loop_count == "unendlich":
                output_lines.append(f"{get_indentation(indentation_level)}while True:\n")
            else:
                output_lines.append(f"{get_indentation(indentation_level)}for i in range({loop_count}):\n")
            indentation_level += 1  # Einrückung erhöhen
        elif code == "endLoop":
            if indentation_level > 0:
                indentation_level -= 1  # Einrückung reduzieren
            output_lines.append(f"{get_indentation(indentation_level)}\n")  # Leerzeile
        elif code == "lampe1":
            output_lines.append(f"{get_indentation(indentation_level)}lampe.turn_on()\n")
            output_lines.append(f"{get_indentation(indentation_level)}time.sleep(0.5)\n")
            output_lines.append(f"{get_indentation(indentation_level)}lampe.turn_off()\n")
            output_lines.append(f"{get_indentation(indentation_level)}time.sleep(0.5)\n")
        elif code == "Pausiere":
            output_lines.append(f"{get_indentation(indentation_level)}time.sleep(1)\n")
 
# Schreibe die generierten Python-Befehle in eine neue Datei
output_file_path = "output_dynamic_loops.py"
with open(output_file_path, "w") as file:
    file.writelines(output_lines)
 
print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")