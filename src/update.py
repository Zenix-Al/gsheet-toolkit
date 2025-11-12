import gspread
from src.manage_actions import prompt_input
from src.helper import format_row, read_csv_with_locale
from datetime import datetime

def main(client, spreadsheet_id, action, config):
    """
    Execute an 'update' action.
    """
    print(f"🟢 Update action started: {action.get('name')}")

    sheet_name = action.get("sheet_name")
    source_type = action.get("source_type", "manual")
    target_cell = action.get("target_cell", "A1")
    column_total = action.get("column_total", 1)
    locale = action.get("locale") or config.get("locale", "US")

    # Open the spreadsheet and worksheet
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
    except Exception as e:
        print(f"❌ Failed to open sheet '{sheet_name}': {e}")
        return

    # ==========================
    # Source: CSV
    # ==========================
    if source_type == "csv":
        csv_file = action.get("csv_file", "")
        if not csv_file.endswith(".csv"):
            csv_file += ".csv"
        csv_path = f"csv/{csv_file}"

        df = read_csv_with_locale(csv_path, locale)
        if df is None:
            return

        values_list = df.values.tolist()

    # ==========================
    # Source: Manual
    # ==========================
    elif source_type == "manual":
        values_list = []
        print("📝 Manual update mode: input one row at a time. Leave blank to stop.")

        # Determine starting row and column from target_cell
        start_row, start_col = gspread.utils.a1_to_rowcol(action.get("target_cell", "A1"))
        current_row = start_row

        while True:
            row_values = []
            print(f"\nEntering values for row {current_row} (starting at column {start_col}):")

            for i in range(column_total):
                # Compute actual column number for display
                col_number = start_col + i
                col_letter = gspread.utils.rowcol_to_a1(1, col_number)[:-1]  # just the column letter

                val = prompt_input(f"Enter value for {col_letter}{current_row}", "")
                row_values.append(val)

            # Stop if all values are blank
            if all(v == "" for v in row_values):
                print("⏹️ Empty row entered. Stopping manual input.")
                break

            values_list.append(row_values)
            current_row += 1  # move to next row for next input


    else:
        print(f"⚠️ Unsupported source_type '{source_type}'. Only 'csv' or 'manual' allowed.")
        return

    # ==========================
    # Update cells
    # ==========================
    # Extract starting row and column from target_cell
    start_row, start_col = gspread.utils.a1_to_rowcol(target_cell)
    current_row = 0
    for i, row_values in enumerate(values_list):
        try:
            formatted_row, notes, formats = format_row(row_values, action.get("cell_formats", []), locale)

            # Compute the current row to update
            current_row = start_row + i

            # Construct A1 notation for the update
            cell_label = gspread.utils.rowcol_to_a1(current_row, start_col)

            # Update the row starting at the calculated row
            worksheet.update(cell_label, [formatted_row], value_input_option="USER_ENTERED")

            # Apply TAGS notes
            for col_index, note_value in notes:
                if note_value:
                    note_cell = gspread.utils.rowcol_to_a1(current_row, start_col + col_index)
                    worksheet.update_note(note_cell, note_value)

            # Apply cell formats
            for j, cell_format in enumerate(formats):
                pattern = cell_format.get("pattern")
                if pattern:
                    fmt_cell = gspread.utils.rowcol_to_a1(current_row, start_col + j)
                    worksheet.format(fmt_cell, {"numberFormat": {"type": "NUMBER", "pattern": pattern}})

            print(f"✅ Updated row at {cell_label}: {formatted_row}")

        except Exception as e:
            print(f"❌ Failed to update row at {current_row}: {e}")
            break


    # ==========================
    # Optionally open sheet
    # ==========================
    if action.get("open_sheet", "n") == "y":
        try:
            gid = worksheet.id
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}&range={target_cell}"
            print(f"\nOpening sheet at target cell:\n{sheet_url}")
            import webbrowser
            webbrowser.open(sheet_url)
        except Exception as e:
            print(f"⚠️ Failed to open sheet in browser: {e}")
