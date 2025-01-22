import easyocr
from PIL import Image
import os

def extract_text_from_image(image_path):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"The image file at {image_path} was not found.")

        reader = easyocr.Reader(['en'])

        result = reader.readtext(image_path)

        extracted_text = " ".join([detection[1] for detection in result])

        if extracted_text:
            print("Extracted Text:")
            print(extracted_text)
            return extracted_text
        else:
            print("No text found in the image.")

    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except Exception as e:
        print(f"An error occurred: {e}")

