import requests
import os

# Create uploads folder if not exists
os.makedirs("uploads", exist_ok=True)

images = [
    ("https://i.imgur.com/XKZQfJq.png", "happy_farmer.png"),
    ("https://i.imgur.com/Sb7wCiG.png", "blue_whale.png"),
    ("https://i.imgur.com/mxv3F8y.png", "sly_fox.png"),
]

for url, filename in images:
    path = os.path.join("uploads", filename)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"✓ Downloaded {filename}")
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")

print("\nDone!")
