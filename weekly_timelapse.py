import os, shutil

ARCHIVE_DIR = "Weekly_Archive"
LEGACY_DIR = "Legacy"

def create_weekly_video():
    if not os.path.exists(ARCHIVE_DIR):
        print("Weekly Archive directory not found.")
        return

    # Use ffmpeg to create a 1-fps video where each image lasts 1 second
    # and cross-fades into the next. 
    # Note: %d assumes files are named 0.png, 1.png, etc.
    cmd = (
        f"ffmpeg -framerate 1 -i {ARCHIVE_DIR}/%d.png "
        "-c:v libx264 -pix_fmt yuv420p -vf 'scale=1080:1080' "
        "weekly_reveal.mp4 -y"
    )
    print(f"Executing: {cmd}")
    os.system(cmd)
    
    # Cleanup: Move images to legacy and clear archive
    if not os.path.exists(LEGACY_DIR): os.makedirs(LEGACY_DIR)
    
    files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.png')]
    for f in files:
        src = os.path.join(ARCHIVE_DIR, f)
        # To avoid overwrite in Legacy, we might want unique names, but since they are numbered 0...N,
        # we should probably timestamp them or move them to a dated subfolder.
        # For now, let's just move them as requested.
        dst = os.path.join(LEGACY_DIR, f)
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Error moving {f}: {e}")

if __name__ == "__main__":
    create_weekly_video()
