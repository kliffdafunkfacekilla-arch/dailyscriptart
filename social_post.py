import os
import json
from atproto import Client
from mastodon import Mastodon

def post_to_bluesky(file_path, text):
    try:
        # Check if environment variables exist
        handle = os.getenv('BSKY_HANDLE')
        password = os.getenv('BSKY_PASSWORD')
        if not handle or not password:
            print("⚠️ BSKY_HANDLE or BSKY_PASSWORD not set. Skipping Bluesky.")
            return

        client = Client()
        client.login(handle, password)
        with open(file_path, 'rb') as f:
            client.send_image(text=text, image=f.read())
        print("✅ Posted to Bluesky")
    except Exception as e:
        print(f"❌ Bluesky Error: {e}")

def post_to_mastodon(file_path, text):
    try:
        token = os.getenv('MASTODON_TOKEN')
        if not token:
            print("⚠️ MASTODON_TOKEN not set. Skipping Mastodon.")
            return

        mastodon = Mastodon(
            access_token=token,
            api_base_url='https://mastodon.social' # Change if using a different instance
        )
        media = mastodon.media_post(file_path)
        mastodon.status_post(text, media_ids=media)
        print("✅ Posted to Mastodon")
    except Exception as e:
        print(f"❌ Mastodon Error: {e}")

if __name__ == "__main__":
    finished_dir = "Daily_Finished"
    if not os.path.exists(finished_dir):
        print(f"❌ Directory {finished_dir} not found.")
        exit(1)

    files = [f for f in os.listdir(finished_dir) if f.endswith('.png')]
    if files:
        # Get the latest generated image
        latest_art = os.path.join(finished_dir, sorted(files)[-1])
        title = os.path.splitext(os.path.basename(latest_art))[0]
        caption = f"FACTORY UPDATE: {title} 🏭 #GenerativeArt #FactoryShift"
        
        print(f"Attempting to post: {latest_art}")
        post_to_bluesky(latest_art, caption)
        post_to_mastodon(latest_art, caption)
    else:
        print("No finished art found to post.")
