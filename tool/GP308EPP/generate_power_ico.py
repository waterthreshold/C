from PIL import Image, ImageDraw

def generate_power_ico():
    # Create a high-res 256x256 canvas with transparency
    size = (256, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 1. Dark circular or rounded badge background
    draw.rounded_rectangle([16, 16, 240, 240], radius=60, fill="#1e1e1e", outline="#2ecc71", width=6)

    # 2. Draw the classic Power Symbol (Standby / Power Icon)
    # Outer broken circle arc (starts at 45° and ends at 315°, leaving the top open)
    draw.arc([68, 68, 188, 188], start=310, end=230, fill="#2ecc71", width=18)
    
    # Vertical line stem pointing up through the break in the circle
    draw.rounded_rectangle([119, 50, 137, 125], radius=9, fill="#2ecc71")

    # 3. Save as a multi-resolution Windows .ico file named 'icon.ico'
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    image.save("icon.ico", format="ICO", sizes=icon_sizes)
    print("Successfully generated 'icon.ico'!")

if __name__ == "__main__":
    generate_power_ico()