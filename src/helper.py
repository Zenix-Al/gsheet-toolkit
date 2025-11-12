from datetime import datetime
import gspread
import pandas as pd
def get_start_col(start_cell="A"):
    """
    Convert start_cell like "B2" or "C" to a 1-indexed column number.
    Only column matters for append.
    """
    if not start_cell:
        start_cell = "A"
    # Convert to uppercase
    start_cell = start_cell.upper()
    # Extract letters only
    col_letters = "".join([c for c in start_cell if c.isalpha()])
    # Convert letters to column number
    col_number = gspread.utils.a1_to_rowcol(f"{col_letters}1")[1]
    return col_number

def read_csv_with_locale(csv_path, locale="US"):
    """
    Reads CSV with appropriate delimiter based on locale.
    """
    delimiter = "," if locale.upper() == "US" else ";"
    try:
        df = pd.read_csv(csv_path, delimiter=";")
        return df
    except Exception as e:
        print(f"❌ Failed to read CSV '{csv_path}' with delimiter '{delimiter}': {e}")
        return None

from datetime import datetime

def format_row(row_values, cell_formats, locale="US"):
    """
    Format a row based on cell_formats and locale.

    Returns:
        formatted_values: list of cell values ready for gspread
        notes: list of (column_index, note) tuples
        formats: list of formatting metadata for each cell (type, pattern)
    """
    formatted_values = []
    notes = []
    formats = []

    formula_sep = "," if locale.upper() == "US" else ";"

    for i, fmt in enumerate(cell_formats):
        fmt_type = fmt.get("type", "text").lower()
        default_val = fmt.get("default", "")
        value = row_values[i] if i < len(row_values) else ""
        cell_format = {"type": fmt_type}

        if fmt_type == "text":
            formatted_values.append(value or default_val)

        elif fmt_type == "number":
            try:
                formatted_values.append(float(value))
            except:
                formatted_values.append(default_val)

        elif fmt_type == "link":
            if value:
                formatted_values.append(f'=HYPERLINK("{value}"{formula_sep} "{default_val}")')
            else:
                formatted_values.append(default_val)

        elif fmt_type == "percent":
            try:
                formatted_values.append(float(value))
            except:
                formatted_values.append(default_val)
            cell_format["pattern"] = "0.00%"

        elif fmt_type == "formula":
            formula_val = value or default_val

            # Ensure formula starts with "="
            if not str(formula_val).startswith("="):
                formula_val = f"={formula_val}"

            formatted_values.append(formula_val)

            # If note contains recognized keywords (like percent or currency),
            # return them as format hints.
            if note := fmt.get("note", "").lower():
                if "percent" in note:
                    formats.append({"type": "NUMBER", "pattern": "0.00%"})
                elif "currency" in note:
                    formats.append({"type": "NUMBER", "pattern": "$#,##0.00"})
                elif "number" in note:
                    formats.append({"type": "NUMBER", "pattern": "0.00"})
                else:
                    formats.append({})
            else:
                formats.append({})


        elif fmt_type == "currency":
            try:
                formatted_values.append(float(value))
            except:
                formatted_values.append(default_val)
            cell_format["pattern"] = "$#,##0.00"

        elif fmt_type == "tags":
            formatted_values.append(default_val)
            notes.append((i, value))

        elif fmt_type == "date":
            if str(value).lower() == "now":
                formatted_values.append(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
            else:
                try:
                    dt = datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
                    formatted_values.append(dt.strftime("%m/%d/%Y %H:%M:%S"))
                except:
                    formatted_values.append(default_val)
            cell_format["pattern"] = "MM/DD/YYYY HH:MM:SS"

        else:
            formatted_values.append(value or default_val)

        formats.append(cell_format)

    return formatted_values, notes, formats
