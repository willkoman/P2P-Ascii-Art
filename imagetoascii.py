import argparse
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog

def rgb_to_ansi(r, g, b):
    """Convert RGB to ANSI color codes for terminal display."""
    return f"\x1b[38;2;{r};{g};{b}m"

def image_to_ascii(image_path, max_width=70, max_height=39, color=False, brightness_threshold=250):
    """Convert an image to ASCII art."""
    # Load the image using PIL
    img = Image.open(image_path)

    # Calculate the new height and width to maintain the aspect ratio
    aspect_ratio = img.width / img.height
    aspect_ratio_char = 2  # Character aspect ratio in most fonts
    new_height = min(max_height, int(img.height * max_width / img.width * aspect_ratio_char))
    new_width = max(max_width, int(img.width * max_height / img.height / aspect_ratio_char))

    # Check if image has an alpha channel (transparency)
    if img.mode == 'RGBA':
        img = img.convert('RGBA')
        # Create a white background to replace transparent areas
        canvas = Image.new('RGB', img.size, (255, 255, 255))
        canvas.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        img = canvas
    elif not color:
        # Convert to grayscale if color is not desired
        img = img.convert("L")

    # Resize the image to the new dimensions
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Define the ASCII characters sorted by perceived luminance
    ascii_chars = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,^'. "
    # Calculate the scale factor for mapping grayscale values to ASCII characters
    scale_factor = (len(ascii_chars) - 1) / 255

    # Convert the image to a numpy array for processing
    img_array = np.array(img)

    # Initialize a list to hold ASCII art lines
    ascii_img = []

    # Generate ASCII art row by row
    for row in img_array:
        row_chars = []
        for pixel in row:
            if color:
                # Skip over pixels brighter than the threshold (likely to be part of the outline)
                if isinstance(pixel, np.ndarray) and all(value > brightness_threshold for value in pixel[:3]):
                    row_chars.append(" ")
                    continue
                # Map the RGB values to ASCII characters with color
                ansi_code = rgb_to_ansi(*pixel[:3])
                char_index = int(sum(pixel[:3]) / 3 * scale_factor)
                char = ascii_chars[char_index]
                row_chars.append(ansi_code + char + "\x1b[0m")  # Append ANSI color code and reset afterwards
            else:
                # For grayscale, directly compare the pixel value with the brightness threshold
                if pixel > brightness_threshold:
                    row_chars.append(" ")
                    continue
                char_index = int(pixel * scale_factor)
                row_chars.append(ascii_chars[char_index])
        ascii_img.append("".join(row_chars))

    return "\n".join(ascii_img)

def main():
    """Main function to handle command-line arguments and user input."""
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter root window

    parser = argparse.ArgumentParser(description='Convert an image to ASCII art.')
    parser.add_argument('-i', '--image_path', type=str, help='Path to the image file', default=None)
    parser.add_argument('-c', '--color', action='store_true', help='Output colored ASCII art')
    args = parser.parse_args()

    # Use a file dialog if no image path is provided via command line
    if args.image_path is None:
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=(("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*"))
        )
        if not file_path:
            print("No image file selected.")
            return  # Exit if no file was selected
        args.image_path = file_path

    # Output the ASCII art
    print(image_to_ascii(args.image_path, color=args.color))

if __name__ == "__main__":
    main()
