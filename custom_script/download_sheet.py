import json
import requests
import os
import shutil

def main():
    # Load config.json
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    spreadsheet_id = config.get("spreadsheet_id")
    if not spreadsheet_id:
        print("❌ 'spreadsheet_id' not found in config.json")
        return

    # Construct download URL dynamically
    download_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"

    # Get filename from spreadsheet title or fallback
    filename = config.get("download_filename", f"{spreadsheet_id}.xlsx")

    temp_filename = f"{filename}.tmp"
    backup_filename = f"{os.path.splitext(filename)[0]}_backup.xlsx"

    print(f"📥 Downloading Excel file from:\n{download_link}")

    try:
        # Download to temporary file
        response = requests.get(download_link, stream=True, timeout=60)
        response.raise_for_status()

        with open(temp_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify file size > 0
        if os.path.getsize(temp_filename) == 0:
            raise ValueError("Downloaded file is empty")

        # Backup existing file (if any)
        if os.path.exists(filename):
            print(f"📦 Creating backup: {backup_filename}")
            shutil.copy2(filename, backup_filename)

        # Replace main file
        shutil.move(temp_filename, filename)
        print(f"✅ Download complete and saved as: {filename}")

    except Exception as e:
        print(f"❌ Download failed: {e}")
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    main()
