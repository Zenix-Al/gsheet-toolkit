import os
from src.manage_actions import prompt_input
import gspread
import webbrowser
from src.helper import get_start_col, read_csv_with_locale, format_row

def main(client, spreadsheet_id, action,config):
    """
    Execute an 'append' action.

    Args:
        client: gspread client
        spreadsheet_id: ID of the spreadsheet
        action: dict from actions.json
    """
    print("🟢 Append action started")

    sheet_name = action.get("sheet_name")
    append_mode = action.get("append_mode", "multiple")
    source_type = action.get("source_type", "manual")
    start_col = action.get("start_cell", "A")
    column_total = action.get("column_total", 1)
    values_length = 0
    locale = action.get("locale") or config.get("locale", "US")
    # Open the spreadsheet and worksheet
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
    except Exception as e:
        print(f"❌ Failed to open sheet '{sheet_name}': {e}")
        return

    # ==========================
    # Mode: CSV
    # ==========================
    if source_type == "csv":
        csv_file = action.get("csv_file", "")
        if not csv_file.endswith(".csv"):
            csv_file += ".csv"
        csv_path = os.path.join("csv", csv_file)

        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return

        try:
            df = read_csv_with_locale(csv_path, locale)
            if df is None:
                return

            values = df.values.tolist()
            values_length = len(values)
            col_number = get_start_col(action.get("start_cell", "A"))
            for row in values:
                # Format row, get notes and formatting metadata
                formatted_row, notes, formats = format_row(row, action.get("cell_formats", []), locale)

                # Pad row if start column > 1
                if col_number > 1:
                    formatted_row = [""] * (col_number - 1) + formatted_row

                print(f"Appending row: {formatted_row}")
                print(f"Note info row: {notes}")
                pause = prompt_input("Press Enter to continue...")
                # Append the row to the worksheet
                worksheet.append_row(formatted_row, value_input_option="USER_ENTERED")

                # Get the last row number after append
                last_row = len(worksheet.get_all_values())

                # Apply TAGS notes
                for col_index, note_value in notes:
                    if note_value:
                        cell_label = gspread.utils.rowcol_to_a1(last_row, col_index + col_number)
                        worksheet.update_note(cell_label, note_value)

                # Apply cell formats
                for i, cell_format in enumerate(formats):
                    col_idx = i + col_number
                    pattern = cell_format.get("pattern")
                    if pattern:
                        cell_label = gspread.utils.rowcol_to_a1(last_row, col_idx)
                        worksheet.format(cell_label, {"numberFormat": {"type": "NUMBER", "pattern": pattern}})




            print(f"✅ Appended {len(values)} rows from {csv_path}")
        except Exception as e:
            print(f"❌ Failed to append CSV data: {e}")
            
    # ==========================
    # Mode: Manual
    # ==========================
    elif source_type == "manual":
        print("📝 Manual append mode: input one row at a time. Leave blank to stop.")
        rows_appended = 0

        while True:
            row_values = []
            for i in range(column_total):
                val = prompt_input(f"Column {i+1} value", "")
                row_values.append(val)

            # Stop if all values are blank
            if all(v == "" for v in row_values):
                break

            try:
                # Format the row and get notes & formatting info
                formatted_row, notes, formats = format_row(row_values, action.get("cell_formats", []), locale)

                # Pad row if start column > 1
                col_number = get_start_col(action.get("start_cell", "A"))
                if col_number > 1:
                    formatted_row = [""] * (col_number - 1) + formatted_row

                # Append row
                worksheet.append_row(formatted_row, value_input_option="USER_ENTERED")

                # Last row index
                last_row = len(worksheet.get_all_values())

                # Apply TAGS notes
                for col_index, note_value in notes:
                    if note_value:
                        cell_label = gspread.utils.rowcol_to_a1(last_row, col_index + col_number)
                        worksheet.update_note(cell_label, note_value)

                # Apply cell formats
                for i, cell_format in enumerate(formats):
                    pattern = cell_format.get("pattern")
                    if pattern:
                        cell_label = gspread.utils.rowcol_to_a1(last_row, i + col_number)
                        worksheet.format(cell_label, {"numberFormat": {"type": "NUMBER", "pattern": pattern}})

                rows_appended += 1

            except Exception as e:
                print(f"❌ Failed to append row: {e}")
                break

        print(f"✅ Finished manual append. Total rows appended: {rows_appended}")


    else:
        print(f"⚠️ Unsupported source_type '{source_type}'. Only 'csv' or 'manual' allowed.")
        return

    if action.get("open_sheet", "n") == "y":
        try:
            # Get worksheet GID
            gid = worksheet.id

            # Calculate first newly appended row
            # If you know how many rows you just appended:
            first_new_row = len(worksheet.get_all_values()) - values_length + 1

            # Construct URL to open at first newly appended row
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}&range=A{first_new_row}"

            print(f"\nOpening sheet at last appended rows:\n{sheet_url}")

            # Open in default web browser
            webbrowser.open(sheet_url)
        except Exception as e:
            print(f"⚠️ Failed to open sheet in browser: {e}")
    return