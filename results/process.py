# python script.py ruta_entrada.png ruta_salida.png --threshold 220

import cv2
import numpy as np
import argparse

def binarize_image(input_path, output_path, th=128):
    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Error: No se pudo leer la imagen.")
        return

    print("Valores de la imagen original:")
    print(np.array_str(image))

    image[image < th] = 0
    image[image >= th] = 255

    cv2.imwrite(output_path, image)
    
    print(f"Imagen binarizada guardada en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binarizar una imagen en escala de grises.")
    parser.add_argument("input_path", type=str, help="Ruta de la imagen de entrada.")
    parser.add_argument("output_path", type=str, help="Ruta de la imagen de salida.")
    parser.add_argument("--threshold", type=int, default=128, help="Valor de umbralización (por defecto 128).")
    
    args = parser.parse_args()
    binarize_image(args.input_path, args.output_path, args.threshold)

