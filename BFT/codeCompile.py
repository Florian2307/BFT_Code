import numpy as np
import os
import subprocess
import camera
import yolo11

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tensor_path = os.path.join(script_dir, 'Tensor.csv')
    tensor = np.atleast_2d(np.loadtxt(tensor_path, delimiter=","))
    confidence_threshold = 0.1

    # Filter irrelavant entries based on confidence (column 4)
    if tensor.shape[1] > 4:
        filtered_tensor = tensor[tensor[:, 4] > confidence_threshold]
    else:
        filtered_tensor = np.empty((0, tensor.shape[1]))

    # Sort primary by y_min and secondary by x_min
    sorted_tensor = filtered_tensor[np.lexsort((filtered_tensor[:, 0], filtered_tensor[:, 1]))]

    codes = (
        "1", "10", "2", "3", "4", "5", "6", "7", "8", "9",
        "Pausiere", "endif", "endLoop", "if", "lampeAus", "lampeEin",
        "loop", "tasterGedruckt", "tasterNichtGedruckt", "unendlich"
    )

    blocks = []
    for row in sorted_tensor:
        block = {
            "x_min": row[0],
            "y_min": row[1],
            "x_max": row[2],
            "y_max": row[3],
            "class_id": int(row[5]),
            "class_name": codes[int(row[5])]
        }
        blocks.append(block)

    code_blocks = [b for b in blocks if b["class_name"] not in ("unendlich", "tasterGedruckt", "tasterNichtGedruckt")]

    # Sortiere die code_blocks nach y_min (Lesereihenfolge von oben nach unten)
    code_blocks.sort(key=lambda b: b["y_min"])

    image_path = camera.capture_image()
    yolo11.create_tensor(image_path, script_dir)
    code = generate_code(code_blocks, blocks)
    code_file_path = write_code_to_file(code)

    subprocess.run(["python", f"{code_file_path}"], check=True)

def find_adjacent_block(block, blocks, mode, tolerance=50, vertical_tolerance=50):

    """
    Sucht das Objekt, das unmittelbar rechts von dem gegebenen Block liegt.
    
      - Der horizontale Abstand zwischen block["x_max"] und candidate["x_min"] 
        ist kleiner als 'tolerance' (kleine negative Abstaende werden akzeptiert,
        wenn sich Blöcke ueberlappen).
      - Der Unterschied der y_min-Werte liegt innerhalb von 'vertical_tolerance'.
    
    Falls mehrere Kandidaten diese Kriterien erfuellen, wird derjenige mit dem
    kleinsten horizontalen Abstand gewaehlt.
    
    Parameter:
      block: Das Ausgangsobjekt (Dictionary).
      blocks: Liste aller Blöcke (die komplette Liste, nicht nur code_blocks).
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

    if not best_candidate and mode == "count":
        return "1"
    elif not best_candidate:
        return "True"

    match mode:
        case "count":
            return {
                19: "unendlich",
                **{i: best_candidate["class_name"] for i in range(10)}
            }.get(best_candidate["class_id"], "1")
        case "taster":
            return {
                "tasterGedruckt": "button.value == 1",
                "tasterNichtGedruckt": "button.value == 0"
            }.get(best_candidate["class_name"], "True")
        case _:
            return None



def generate_code(code_blocks, blocks):
    output_lines = [
        "from gpiozero import LED, Button\nfrom time import sleep\n\nled = LED(17)\nbutton = Button(3)\n\n"
    ]
    indentation_level = 0

    action_map = {
        "loop": handle_loop,
        "endLoop": handle_end_loop,
        "if": handle_if,
        "endif": handle_end_if,
        "lampeEin": handle_lampe_ein,
        "lampeAus": handle_lampe_aus,
        "Pausiere": handle_pausiere,
    }

    for block in code_blocks:
        code = block["class_name"]
        handler = action_map.get(code)
        if handler:
            output_lines = handler(block, blocks, output_lines, indentation_level)
            if code in ["loop", "if"]:
                indentation_level += 1
            elif code in ["endLoop", "endIf"]:
                indentation_level -= 1

    return "".join(output_lines)


def handle_loop(block, blocks, output_lines, indentation_level):
    loop_count = find_adjacent_block(block, blocks, mode="count", tolerance=50, vertical_tolerance=50)
    if loop_count == "unendlich" or loop_count == None:
        output_lines.append(f"{get_indentation(indentation_level)}while True:\n")
    else:
        output_lines.append(f"{get_indentation(indentation_level)}for i in range({loop_count}):\n")

    return output_lines


def handle_end_loop(block, blocks, output_lines, indentation_level):
    if indentation_level > 0:
        indentation_level -= 1

    return output_lines


def handle_if(block, blocks, output_lines, indentation_level):
    condition = find_adjacent_block(block, blocks, mode="taster", tolerance=50, vertical_tolerance=50)
    output_lines.append(f"{get_indentation(indentation_level)}if {condition}:\n")

    return output_lines


def handle_end_if(block, blocks, output_lines, indentation_level):
    if indentation_level > 0:
        indentation_level -= 1

    return output_lines


def handle_lampe_ein(block, blocks, output_lines, indentation_level):
    output_lines.append(f"{get_indentation(indentation_level)}led.on()\n")

    return output_lines


def handle_lampe_aus(block, blocks, output_lines, indentation_level):
    output_lines.append(f"{get_indentation(indentation_level)}led.off()\n")

    return output_lines


def handle_pausiere(block, blocks, output_lines, indentation_level):
    paus_count = find_adjacent_block(block, blocks, mode="count", tolerance=50, vertical_tolerance=50)
    if paus_count == "unendlich":
        paus_count = "1"
    elif paus_count == None:
        paus_count = "0"
    output_lines.append(f"{get_indentation(indentation_level)}sleep({paus_count})\n")

    return output_lines


def get_indentation(level):
    return "    " * level


def write_code_to_file(code):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(script_dir, "final.py")
    with open(output_file_path, "w") as file:
        file.writelines(code)

    print(f"Das Python-File wurde erfolgreich unter '{output_file_path}' erstellt.")
    return output_file_path

if __name__ == "__main__":
    main()
