## gsheet-toolkit

A **modular Google Sheets automation toolkit** that lets you append, update, and edit spreadsheet data dynamically — all from the command line.
Actions are saved in `actions.json`, and you can even plug in your own custom scripts for backups, local scanning, or sheet downloads.

---

### 🚀 Features

- **Append data** — Add rows from CSV or manual input
- **Update cells** — Change specific ranges or formulas
- **Custom scripts** — Extend functionality (e.g., backup, folder scan, download)
- **Config-based workflow** — Reuse credentials, spreadsheet IDs, and sheet info
- **CSV integration** — Feed any CSV directly into Google Sheets
- **Locale-aware formatting** — Handles text, percent, currency, date, tags, links, and formulas

---

### 🧰 Requirements

- Python **3.8+**
- Google Cloud **Service Account** with Sheets + Drive API access
- Dependencies:

  ```bash
  pip install pandas gspread google-auth openpyxl
  ```

---

### ⚙️ Setup

1. **Create a Google Cloud Project**

   - Enable **Google Sheets API** and **Google Drive API**
   - Create a **Service Account**
   - Download your key as `service_account.json`

   [Google Workspace Credentials Guide](https://developers.google.com/workspace/guides/create-credentials)

2. **Share your Google Sheet**

   - Share it with your service account email
   - Grant **Editor** access

3. **Prepare your configuration**

   - Copy `config_example.json` → rename to `config.json`
   - Example:

     ```json
     {
       "credentials_file": "service_account.json",
       "spreadsheet_id": "your_spreadsheet_id_here",
       "locale": "EU / US",
       "version": "0.1.0"
     }
     ```

4. **Run the Toolkit**

   ```bash
   python main.py
   ```

   You’ll be prompted to select an action — append, update, or run a custom script.

---

### 🔧 Actions System

Actions are stored in **`actions.json`**, allowing you to save and reuse configurations like:

#### Example — Append from CSV

```json
{
  "name": "main_database_append",
  "action": "append",
  "sheet_name": "Main",
  "sheet_id": 123456,
  "append_mode": "multiple",
  "source_type": "csv",
  "csv_file": "main",
  "start_cell": "A",
  "column_total": 7,
  "open_sheet": "y",
  "cell_formats": [
    {
      "type": "text",
      "default": "Title",
      "note": ""
    },
    {
      "type": "link",
      "default": "Link",
      "note": ""
    }
  ]
}
```

#### Example — Update a Cell

```json
{
  "name": "progress_updater",
  "action": "update",
  "sheet_name": "DASHBOARD",
  "target_cell": "B7",
  "cell_formats": [{ "type": "formula", "default": "=SUM(A1:A5)", "note": "", "pattern": "0.00%" }]
}
```

#### Example — Custom Script

```json
{
  "name": "download_backup",
  "action": "custom_script",
  "custom_script": "sheet_backup.py"
}
```

Custom scripts live in `/custom_script` and can be run just like any other action.

---

### Example Custom Scripts

- **`download_sheet.py`** — Download and back up the sheet as `.xlsx`

---

### Notes

- Each sheet format (percent, link, formula, etc.) is automatically handled.
- Errors are logged directly in the console — no silent failures.
- Keep your service account key private (`service_account.json`).

---

### 📁 Folder Structure

```
project_root/
├── main.py
├── config.json
├── actions.json
├── src/
│   ├── append.py
│   ├── update.py
│   ├── helper.py
│   ├── manage_actions.py
├── custom_script/
│   ├── playing_uploader.py
├── csv/
│   ├── your.csv
└── README.md
```

---

### 📜 License

**MIT License © 2025**

---

Would you like me to add a small **“Quick Action Creation”** section (like a guide to quickly make a new append/update/custom action via the prompt)?
It’d be perfect for onboarding or open-sourcing this.
