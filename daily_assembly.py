import os, json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

MEMORY_FILE = "factory_memory.json"
QUEUE_DIR = "Daily_Queue"
FINISHED_DIR = "Daily_Finished"
ARCHIVE_DIR = "Weekly_Archive"
LOG_FILE = "factory_log.txt"

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
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            # Fallback for Windows or common Pillow installs
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # 3. Calculate position (Bottom Right with 20px margin)
    left, top, right, bottom = font.getbbox(text)
    text_w, text_h = right - left, bottom - top
    
    margin = 50 # Increased margin for the larger composite
    pos = (image_obj.width - text_w - margin, image_obj.height - text_h - margin)

    # 4. Draw the text with 50% opacity (Alpha = 128)
    draw.text(pos, text, font=font, fill=(255, 255, 255, 128))

    # 5. Composite the watermark onto the original
    return Image.alpha_composite(image_obj.convert("RGBA"), watermark).convert("RGB")

def create_daily_log(title, word_list):
    log_entry = f"--- {title} ---\nDate: {datetime.now()}\nWords: {', '.join(word_list)}\n\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(f"Log updated: {LOG_FILE}")

def build_daily_grid():
    if not os.path.exists(FINISHED_DIR): os.makedirs(FINISHED_DIR)
    if not os.path.exists(ARCHIVE_DIR): os.makedirs(ARCHIVE_DIR)

    queue = sorted([f for f in os.listdir(QUEUE_DIR) if f.endswith('.png')])
    if len(queue) < 24: 
        print(f"Not enough images for daily grid. Current count: {len(queue)}")
        return 

    # Create 6x4 Grid
    master = Image.new('RGB', (4000, 6000)) 
    for i, img_path in enumerate(queue[:24]):
        img = Image.open(f"{QUEUE_DIR}/{img_path}").resize((1000, 1000))
        x = (i % 4) * 1000
        y = (i // 4) * 1000
        master.paste(img, (x, y))

    # Title Logic
    try:
        with open(MEMORY_FILE, "r") as f:
            mem = json.load(f)
        pool = mem["word_pool"]
        title_words = [pool[-44], pool[-43], pool[-2], pool[-1]]
        title = "-".join(title_words).upper()
    except Exception as e:
        print(f"Title generation error: {e}. Using fallback.")
        title = "DAILY-COLLECTION-UNKNOWN"
        title_words = ["DAILY", "COLLECTION"]
    
    # Apply Advanced Watermark
    watermarked_master = apply_factory_watermark(master, f"FACTORY MASTERPIECE: {title}")
    
    save_path = f"{FINISHED_DIR}/{title}.png"
    watermarked_master.save(save_path)
    print(f"Daily grid saved: {save_path}")
    
    # Update Log
    create_daily_log(title, title_words)
    
    # Archive for Weekly
    for f in queue[:24]:
        count = len(os.listdir(ARCHIVE_DIR))
        os.rename(f"{QUEUE_DIR}/{f}", f"{ARCHIVE_DIR}/{count}.png")

if __name__ == "__main__":
    build_daily_grid()
