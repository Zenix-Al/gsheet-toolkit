## gsheet-toolkit

A lightweight Python toolkit for managing Google Sheets update, append, edit cells, and back up your sheets using simple scripts and CSV input.
An edit maybe required to make it do what you wanted.

---

### Features

- Update or replace an entire Google Sheet from a CSV file
- Append new rows from a CSV input
- Update specific cells
- Back up your Google Sheet locally
- Configuration via `config.json` for easy reuse

---

### ⚙️ Requirements

- Python 3.8+
- Google Cloud service account (with Sheets and Drive API access)
- Dependencies (install via pip):

  ```bash
  pip install pandas gspread google-auth
  ```

---

### 🪄 Setup

1. **Create a Google Cloud Project**

   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Enable **Google Sheets API** and **Google Drive API**.
   - Create a **Service Account** under “APIs & Services → Credentials”.
   - Download the **service_account.json** key file.

   👉 See Google’s official guide here:
   [https://developers.google.com/workspace/guides/create-credentials](https://developers.google.com/workspace/guides/create-credentials)

2. **Share your target Google Sheet**

   - Open your Google Sheet.
   - Click **Share** → add the _client email_ from your service account JSON file.
   - Give it **Editor** permission.

3. **Prepare your configuration file**

   - Copy `config_example.json` → rename to `config.json`.
   - Update it with your own values

4. **Prepare your CSV file**

   - Use the example at `example_data.csv.txt` as a template.
   - Rename it to `data.csv` or update the filename in your `config.json`.
   - Make sure your delimiter (`;` or `,`) matches your script.

---

### 🧩 Example Workflow

1. Edit your `data.csv` file with new entries.
2. Run `input.py` to push them to Google Sheets.
3. When needed, run `backup_sheet.py` to download a copy.

---

### 🧠 Notes

- All CSV updates are validated before sending to the sheet.
- You can modify `delimiter`, `columns`, or notes logic inside each script.
- Keep your `service_account.json` **private** — do not upload it to GitHub.

---

### 📜 License

MIT License © 2025
