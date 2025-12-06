import os
import requests
import random
import tarfile
import shutil

# --- Configuration ---
# URL for the list of validation set archives
K400_VAL_URL_LIST = "https://s3.amazonaws.com/kinetics/400/val/k400_val_path.txt"

# Directories
TEMP_DOWNLOAD_DIR = "kinetics_temp_downloads" # For .tar.gz files
EXTRACT_DIR = "kinetics_full_extracted"     # For all extracted videos
SAMPLES_DIR = "kinetics_samples"            # Final clean folder with your clips

# Sampling controls
NUM_ARCHIVES_TO_DOWNLOAD = 3  # How many .tar.gz files to download (each is one action class)
MAX_CLIPS_FINAL = 15          # The final number of clips you want in your sample folder

def setup_kinetics_samples():
    """
    Downloads and extracts a small, random sample from the Kinetics-400 dataset.
    """
    print("--- AIris Kinetics-400 Sampler ---")

    # --- Step 1: Fetch the list of all video archives ---
    print(f"\n[1/5] 📥 Fetching the list of video archives from {K400_VAL_URL_LIST}...")
    try:
        response = requests.get(K400_VAL_URL_LIST)
        response.raise_for_status()  # Raises an exception for bad status codes
        archive_urls = response.text.strip().split('\n')
        print(f"✅ Found {len(archive_urls)} total archives in the validation set.")
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch the URL list. Please check your connection. Details: {e}")
        return

    # --- Step 2: Select a random subset of archives to download ---
    if len(archive_urls) < NUM_ARCHIVES_TO_DOWNLOAD:
        print(f"[Warning] Not enough archives available. Will download all {len(archive_urls)}.")
        selected_urls = archive_urls
    else:
        selected_urls = random.sample(archive_urls, NUM_ARCHIVES_TO_DOWNLOAD)
    
    print(f"\n[2/5] 🎲 Randomly selected {len(selected_urls)} archives to download.")

    # --- Step 3: Download and extract the selected archives ---
    os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    print("\n[3/5] 📦 Downloading and extracting archives... (This may take a few minutes)")
    all_extracted_videos = []

    for url in selected_urls:
        filename = os.path.basename(url)
        archive_path = os.path.join(TEMP_DOWNLOAD_DIR, filename)
        
        try:
            print(f"  -> Downloading {filename}...")
            # Download with streaming to handle large files
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(archive_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            print(f"  -> Extracting {filename}...")
            with tarfile.open(archive_path, "r:gz") as tar:
                # We need to find the video files during extraction
                for member in tar.getmembers():
                    if member.isfile() and any(member.name.lower().endswith(ext) for ext in ['.mp4', '.avi']):
                        all_extracted_videos.append(os.path.join(EXTRACT_DIR, member.name))
                tar.extractall(path=EXTRACT_DIR)

            # Clean up the downloaded archive immediately to save space
            os.remove(archive_path)
            print(f"  ✅ Extracted and cleaned up {filename}.")
        
        except Exception as e:
            print(f"  [ERROR] Failed to process {filename}. Skipping. Details: {e}")
            continue
            
    # Clean up the temporary download directory
    shutil.rmtree(TEMP_DOWNLOAD_DIR)

    if not all_extracted_videos:
        print("[ERROR] No video files were successfully extracted. Please try again.")
        return

    # --- Step 4: Select the final random sample from all extracted videos ---
    print(f"\n[4/5] ✨ Selecting final {MAX_CLIPS_FINAL} clips from {len(all_extracted_videos)} extracted videos.")
    if os.path.exists(SAMPLES_DIR):
        shutil.rmtree(SAMPLES_DIR) # Clean up old samples
    os.makedirs(SAMPLES_DIR)

    if len(all_extracted_videos) < MAX_CLIPS_FINAL:
        print(f"  [Warning] Extracted fewer videos than requested. Using all {len(all_extracted_videos)} videos.")
        final_clips = all_extracted_videos
    else:
        final_clips = random.sample(all_extracted_videos, MAX_CLIPS_FINAL)

    # --- Step 5: Copy final clips to the clean sample directory ---
    print("\n[5/5] 🚚 Copying final samples to the 'kinetics_samples' directory...")
    for video_path in final_clips:
        if os.path.exists(video_path):
            shutil.copy(video_path, SAMPLES_DIR)
        else:
            print(f"  [Warning] Source file not found, cannot copy: {video_path}")
            
    # Final cleanup of the large extraction folder
    print(f"\n[Recommendation] You can now delete the large '{EXTRACT_DIR}' folder to save space.")

    print("\n--- Sample Setup Complete! ---")
    print(f"✅ Successfully created a sample set of {len(os.listdir(SAMPLES_DIR))} video clips in '{SAMPLES_DIR}/'.")
    print("You can now run 'python app.py' and test with these videos.")

if __name__ == "__main__":
    setup_kinetics_samples()