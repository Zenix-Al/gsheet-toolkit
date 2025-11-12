import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import webbrowser

# === Load config ===
with open("config.json") as f:
    cfg = json.load(f)

# === Auth ===
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(cfg["credentials_file"], scopes=SCOPES)
client = gspread.authorize(creds)

# === Open Sheet ===
sheet = client.open_by_key(cfg["spreadsheet_id"])
worksheet = sheet.worksheet(cfg["worksheet_name"])

# === Load CSV ===
df = pd.read_csv(cfg["csv_file"],delimiter=';')

# === Prepare rows ===
rows_to_append = []

for idx, row in df.iterrows():
    title = str(row.get("title", "")).strip()
    url = str(row.get("link", "")).strip()
    interest = str(row.get("interest", "")).strip()
    tags = str(row.get("tags", "")).strip()
    note = str(row.get("note", "")).strip()
    isfavorite = str(row.get("isfavorite", "FALSE")).upper()
    
    # Validation
    values_to_check = [title, url, interest, tags, note, isfavorite]

    # Skip if any value is empty or "NONE"
    if not title or not url or any(v is None or str(v).upper() == "NONE" for v in values_to_check):
        print(f"Skipping invalid row {idx}: {row.to_dict()}")
        continue


    # Timestamp
    date_added = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Link formula
    link_formula = f'=HYPERLINK("{url}"; "Link")'

    # Append row data (tags will be added as a note later)
    rows_to_append.append({
        "values": [title, link_formula, interest, "TAGS", note, date_added, isfavorite],
        "tags_note": tags
    })

# === Preview rows ===
print("Prepared rows for append:\n")
headers = ["Title", "Link", "Interest", "Tags(Note)", "Note", "Date Added", "IsFavorite"]
print("{:<20} {:<30} {:<8} {:<20} {:<25} {:<20} {:<10}".format(*headers))
print("-" * 140)

for r in rows_to_append:
    vals = r["values"].copy()
    # Replace column 4 (tags) with tags_note for preview
    vals[3] = r["tags_note"]
    print("{:<20} {:<30} {:<8} {:<20} {:<25} {:<20} {:<10}".format(*vals))


# === Confirm commit ===
confirm = input("Commit these rows to Google Sheet? (y/n): ").strip().lower()
if confirm != "y":
    print("Aborted.")
    exit()

# === Append rows and add notes ===
for r in rows_to_append:
    worksheet.append_row(r["values"], value_input_option="USER_ENTERED")
    # Get the last row number
    last_row = len(worksheet.get_all_values())
    # Add tags as a note in column 4 (D)
    worksheet.update_note(f"D{last_row}", r["tags_note"])

print("All rows committed successfully!")

# === Open Google Sheet at last appended row ===
# Get worksheet GID
gid = worksheet.id

# Calculate first newly appended row
first_new_row = len(worksheet.get_all_values()) - len(rows_to_append) + 1

# Construct URL
sheet_url = f"https://docs.google.com/spreadsheets/d/{cfg['spreadsheet_id']}/edit#gid={gid}&range=A{first_new_row}"

print(f"\nOpening sheet at last appended rows:\n{sheet_url}")

# Open in default web browser
webbrowser.open(sheet_url)
