import requests, random, os, json, time
from PIL import Image, ImageDraw, ImageFont
import io

MEMORY_FILE = "factory_memory.json"
QUEUE_DIR = "Daily_Queue"

def apply_factory_watermark(image_obj, text="FACTORY-13"):
    """
    Applies a semi-transparent text watermark to the bottom-right corner.
    """
    # 1. Create a transparent overlay the same size as the image
    watermark = Image.new("RGBA", image_obj.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    
    # 2. Choose font size relative to image height (e.g., 3% of height)
    font_size = int(image_obj.height * 0.03)
    try:
        # Standard location for Linux/Ubuntu runners
        # Falling back to DejaVuSans-Bold or similar
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            # Try Windows common path if local
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # 3. Calculate position (Bottom Right with 20px margin)
    left, top, right, bottom = font.getbbox(text)
    text_w, text_h = right - left, bottom - top
    
    margin = 20
    pos = (image_obj.width - text_w - margin, image_obj.height - text_h - margin)

    # 4. Draw the text with 50% opacity (Alpha = 128)
    draw.text(pos, text, font=font, fill=(255, 255, 255, 128))

    # 5. Composite the watermark onto the original
    return Image.alpha_composite(image_obj.convert("RGBA"), watermark).convert("RGB")

def generate_your_name_logic():
    if not os.path.exists(MEMORY_FILE):
        return "Unknown Factory"
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    pool = data.get("word_pool", ["Art", "Factory"])
    name_parts = random.sample(pool, 2)
    new_name = f"{name_parts[0]} {name_parts[1]}"
    pool.append(new_name.replace(" ", ""))
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return new_name

def generate_hourly_image(prompt_text, retries=3):
    if not os.path.exists(QUEUE_DIR): os.makedirs(QUEUE_DIR)
    
    clean_prompt = "".join(c for c in prompt_text if c.isalnum() or c==' ').strip()
    url = f"https://image.pollinations.ai/prompt/{clean_prompt.replace(' ', '%20')}?width=512&height=512&nologo=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(retries):
        print(f"Requesting (Attempt {attempt+1}): {url}")
        try:
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content)).convert('RGB')
                
                # Apply high-end watermark
                img = apply_factory_watermark(img)
                
                timestamp = len(os.listdir(QUEUE_DIR))
                img_path = f"{QUEUE_DIR}/frame_{timestamp:02d}.png"
                img.save(img_path)
                print(f"Successfully generated and watermarked: {prompt_text} -> {img_path}")
                return True
            else:
                print(f"API Error: Status Code {response.status_code}")
                if response.status_code == 502:
                    time.sleep(5)
                else:
                    break
        except Exception as e:
            print(f"API Error: {e}")
            time.sleep(5)
            
    return False

if __name__ == "__main__":
    name = generate_your_name_logic()
    print(f"Generated Name: {name}")
    generate_hourly_image(name)
