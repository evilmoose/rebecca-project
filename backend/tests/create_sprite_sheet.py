from PIL import Image

# List of individual images
images = [
    "backend/tests/images/rebecca-neutral.png",
    "backend/tests/images/rebecca-A-I.png",
    "backend/tests/images/rebecca-O.png",
    "backend/tests/images/rebecca-U.png",
    "backend/tests/images/rebecca-E.png",
    "backend/tests/images/rebecca-F.png",
    "backend/tests/images/rebecca-L.png",
    "backend/tests/images/rebecca-B-M-P.png",
    "backend/tests/images/rebecca-Q-W.png",
    "backend/tests/images/rebecca-CH-J-SH.png",
    "backend/tests/images/rebecca-TH.png"
]

# Load images and get dimensions
frames = [Image.open(img) for img in images]
width, height = frames[0].size

# Calculate sprite sheet dimensions (4 columns, 3 rows)
columns = 4
rows = 3
sheet_width = columns * width
sheet_height = rows * height

# Create blank sprite sheet
sprite_sheet = Image.new("RGBA", (sheet_width, sheet_height))

# Paste each image into the correct position
for index, frame in enumerate(frames):
    x = (index % columns) * width  # Calculate x position
    y = (index // columns) * height  # Calculate y position
    sprite_sheet.paste(frame, (x, y))

# Save the sprite sheet
sprite_sheet.save("sprite_sheet.png")
print("Sprite sheet created successfully!")
