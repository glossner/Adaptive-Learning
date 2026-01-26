import requests
import os

URL = "https://raw.githubusercontent.com/SirFizX/standards-data/refs/heads/master/clean-data/CC/math/CC-math-0.8.0.json"
OUTPUT = "/home/jglossner/Adaptive-Learning/backend/data/math_standards_raw.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download():
    print(f"Downloading {URL}...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        with open(OUTPUT, "wb") as f:
            f.write(response.content)
            
        print(f"Successfully saved to {OUTPUT} ({len(response.content)} bytes)")
        
    except Exception as e:
        print(f"Error downloading: {e}")

if __name__ == "__main__":
    download()
