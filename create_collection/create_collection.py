"""
Author: Tobias Kuhn
Date: 6. Mai 2025
Description: This script creates a collection of photos for training a model.
Version: 1.0
"""

import os, sys
from picamera2 import Picamera2
from time import sleep

def create_collection_dir():
    """
    Creates a directory for the collection if it doesn't exist.
    Returns the absolute path of the collection directory.
    """

    path = os.path.dirname(os.path.abspath(__file__))
    collection_path = os.path.join(path, "collection")

    try:
        os.chdir(collection_path)
    except FileNotFoundError:
        os.chdir(path)
        os.mkdir("collection")
        os.chdir("collection")
    
    return os.path.abspath(os.getcwd())

def do_photo(image_path):
    """
    Expect: image_path (str): Path to save the image.
    """
    picam2 = Picamera2()
    picam2.start()
    picam2.capture_file(image_path)
    picam2.stop()
    picam2.close()

def main():
    collection_path = create_collection_dir()
    print(f"Collection path: {collection_path}")
    img_name = input("Tippe den Namen des Bildes ein (z.B. codeblock_Warte): ")

    for i in range(3):
        print(i)
        file_name = f"{img_name}_{i}.png"
        image_path = os.path.join(collection_path, file_name)
        
        do_photo(image_path)
        sleep(1)


if __name__ == "__main__":
    main()