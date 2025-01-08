import sys, os
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_symbols = "$@B%8&WM#*oahkbdpqwmZ_QLCJUYX123456789zcvunxrjft/\\|()1[]?-_+~<>i!lI;:,\"^`'. "
# _symbols = "░▀█▀▒██▀░▀▄▀░▀█▀░░▒█▀▒▄▀▄░█▄░█░▄▀▀░▀▄▀░▒█▒░█▄▄░█▒█░▒█▒▒░░█▀░█▀█░█▒▀█░▀▄▄░▒█▒"
# _symbols = "&'()*+,-./"

# Character size (empirical value)
char_width = 10 
char_height = 10 

def calculate_char_brightness(symbols):
    """
    Calculates the average brightness of each ASCII character in the symbol list.
    """
    brightness_values = []
    for char in symbols:
        canvas = Image.new('L', (50, 50), color=255) # Luminance
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default()
        draw.text((char_width, char_height), char, font=font, fill=0)
        brightness = np.mean(np.array(canvas))
        brightness_values.append(brightness)
    return brightness_values

def convert_image_to_ascii(image, ascii_cols, scale, symbols):
    """
    Converts an image into ASCII art, ensuring the entire image is covered and not cropped.
    """
    image_width, image_height = image.size

    # Adjust the number of columns to fit the image and the scale
    ascii_width = image_width / ascii_cols # Width of each block
    ascii_height = ascii_width / scale     # Height of each block based on the scale

    # Calculate the number of rows (doesn't crop the image, rounding up)
    ascii_rows = int(np.ceil(image_height / ascii_height)) # Rounding up to ensure the whole image is covered

    brightness_values = calculate_char_brightness(symbols)
    sorted_symbols = [symbols[idx] for idx in np.argsort(brightness_values)]

    ascii_img = []
    for j in range(ascii_rows):
        y1 = int(j * ascii_height)
        y2 = int((j + 1) * ascii_height)

        # Adjust the last row so it isn't cropped
        if y2 > image_height:
            y2 = image_height

        ascii_row = ""
        for i in range(ascii_cols):
            x1 = int(i * ascii_width)
            x2 = int((i + 1) * ascii_width)

            # Crop the image into blocks and calculate the average brightness
            img_tile = image.crop((x1, y1, x2, y2))
            avg_brightness = int(np.mean(np.array(img_tile)))
            char_index = int((avg_brightness * (len(sorted_symbols) - 1)) / 255)
            ascii_row += sorted_symbols[char_index]

        ascii_img.append(ascii_row)

    return ascii_img

def save_ascii_as_image(ascii_art, output_file, font_color='black', font_type='default'):
    """
    Saves the ASCII art into a PNG image with the same dimensions as the generated text.
    """
    try:
        if font_type == 'default':
            font = ImageFont.load_default() 
        else:
            font = ImageFont.truetype(f"./fonts/{font_type}.ttf", size=char_height) 
    except IOError as e:
        print(f"Error loading font '{font_type}': {e}. Using default font.")
        font = ImageFont.load_default()

    if font_color == 'black':
        text_color = 0  
        bg_color = 255  
    elif font_color == 'white':
        text_color = 255 
        bg_color = 0     
    else:
        text_color = font_color
        bg_color = 255 

    # Force scale to keep the aspect ratio unchanged
    scale = 1

    # Calculate the dimensions of the final image based on the text
    ascii_img_width = len(ascii_art[0]) * char_width # Image width in pixels
    ascii_img_height = len(ascii_art) * char_height  # Image height in pixels

    print(f"ASCII art dimensions (text): {len(ascii_art[0])} columns x {len(ascii_art)} rows")
    print(f"Resulting image dimensions: {ascii_img_width} x {ascii_img_height} pixels")
    print(f"Character size: {char_width} x {char_height} pixels")

    # Create an image with the appropriate size
    img = Image.new('L', (ascii_img_width, ascii_img_height), color=bg_color) 
    draw = ImageDraw.Draw(img)

    # Place the characters in the image
    y_offset = 0
    for line in ascii_art:
        x_offset = 0
        for char in line:
            # Draw each character at its position
            draw.text((x_offset, y_offset), char, fill=text_color, font=font) 
            x_offset += char_width # Move to the next character
        y_offset += char_height    # Move to the next row

    # Crop any empty border on the image to remove any unnecessary white space
    img = img.crop((0, 0, ascii_img_width, ascii_img_height)) 

    img.save(output_file)

def save_ascii_text(ascii_art, text_file):
    """
    Saves the ASCII art into a text file.
    """
    with open(text_file, 'w') as f:
        for row in ascii_art:
            f.write(row + '\n')

def print_custom_help():
    """
    Prints a custom help message.
    """
    help_text = """
    asciimage.py

    A Python program to convert images into ASCII representations, and vice versa.

    Usage:
        python asciimage.py --file <image_path> [--symbols <string>] [--scale <float>] [--ascii_cols <int>] [--out=<output_type>] [--font_type=<font>]

    Options:
        --file       Path to the input image file (required).
        --scale      Scale factor for aspect ratio (default: 0.5, a good value to visually maintain the ratio of ASCII characters).
        --ascii_cols Number of ASCII columns (default: 100).
        --out        Output type: text (default) or image (creates PNG).
        --font_type  Characters color for image, the background will be the opposite.
        --font_type  Font type for output image: default, arial, dirtydoz, fudd, times or times_new_roman.
        --symbols    Custom ASCII characters to use (optional, e.g. --symbols dfsg256B%8).

    Author:
        agarnung
    """
    print(help_text)

def main():
    global _symbols
    
    if '--help' in sys.argv:
        print_custom_help()
        sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='imgFile', required=True)
    parser.add_argument('--scale', dest='scale', required=False, default="auto")
    parser.add_argument('--ascii_cols', dest='ascii_cols', required=False)
    parser.add_argument('--out', dest='out', required=False)
    parser.add_argument('--font_color', dest='font_color', required=False, default='black') 
    parser.add_argument('--font_type', dest='font_type', required=False, default='default') 
    parser.add_argument('--symbols', dest='symbols', required=False)

    args = parser.parse_args()

    output_dir = str(args.out) if args.out else './results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image = Image.open(args.imgFile).convert('L')
    ascii_cols = int(args.ascii_cols) if args.ascii_cols else 100
    scale = float(args.scale) if args.scale != "auto" else 0.43
    _symbols = str(args.symbols) if args.symbols else _symbols

    print(f"Input image dimensions: {image.size[0]} x {image.size[1]}")
    print("Generating ASCII art...")

    ascii_art = convert_image_to_ascii(image, ascii_cols, scale, _symbols)

    text_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(args.imgFile))[0]}_ascii.txt")
    save_ascii_text(ascii_art, text_file)

    output_image = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(args.imgFile))[0]}_ascii.png")
    save_ascii_as_image(convert_image_to_ascii(image, ascii_cols, 1, _symbols), output_image, args.font_color, args.font_type)  # Changed here

if __name__ == '__main__':
    main()
