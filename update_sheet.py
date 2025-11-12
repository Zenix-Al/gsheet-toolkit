import os
import re
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re

# === Load config ===
with open("config.json") as f:
    cfg = json.load(f)

# === CONFIG ===
FOLDER_PATH = cfg.get("folder_path", "./games")
CSV_FILE = cfg.get("csv_playing", "playing.csv")
BLACKLIST = cfg.get("blacklist", [])  # list of allowed folder names, optional

# === AUTH ===
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(cfg["credentials_file"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(cfg["spreadsheet_id"])
worksheet = sheet.worksheet(cfg["worksheet_name_playing"])

# === FUNCTION: Clean folder name ===
def clean_title(name: str) -> str:
    # remove version-style patterns (v1.2.3, ver2.0, or standalone 1.2.3)
    name = re.sub(
        r'([_\-\s]|^)(v|ver|version)?\s*\d+(\.\d+){1,}',
        '',
        name,
        flags=re.IGNORECASE
    )

    # replace underscores/dashes with spaces
    name = name.replace('_', ' ').replace('-', ' ')

    # remove unwanted words like "ver", "version", "dlsite" (case-insensitive)
    name = re.sub(r'\b(ver|version|dlsite)\b', '', name, flags=re.IGNORECASE)

    # clean up double spaces
    name = re.sub(r'\s+', ' ', name).strip()

    return name

# === SCAN FOLDER ===
entries = []
for item in os.listdir(FOLDER_PATH):
    full_path = os.path.join(FOLDER_PATH, item)
    if os.path.isdir(full_path):
        if BLACKLIST and item in BLACKLIST:
            continue
        cleaned = clean_title(item)
        entries.append(cleaned)

# === CREATE DATAFRAME ===
df = pd.DataFrame(entries, columns=["Title"])

# === SHOW PREVIEW ===
print("\n📄 Preview of data to be uploaded:\n")
print(df.head(10))
print(f"\nTotal entries: {len(df)}")
confirm = input("\nProceed to update Google Sheet? (y/n): ").strip().lower()

if confirm == 'y':
    # save to CSV
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ CSV saved: {CSV_FILE}")

    # clear & update sheet
    worksheet.batch_clear(['A2:A100'])
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheet updated successfully!")
else:
    print("❌ Update cancelled.")
