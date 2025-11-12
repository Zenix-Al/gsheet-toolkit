import gspread
from google.oauth2.service_account import Credentials
import json

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

# === Open spreadsheet and DASHBOARD sheet ===
sheet = client.open_by_key(cfg["spreadsheet_id"])
dashboard = sheet.worksheet("DASHBOARD")

# === Get current formula in B7 ===
current_formula = dashboard.get('B7', value_render_option='FORMULA')[0][0]
print(f"Current formula in B7: {current_formula}")

# === Prompt user for new formula ===
new_formula = input("Enter new formula for B7 (include '=' at start): ").strip()

if new_formula:
    dashboard.update('B7', [[new_formula]])
    dashboard.format('B7', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}})
    print(f"B7 updated to: {new_formula} (format: percentage)")
else:
    print("No formula entered. B7 not changed.")
