# src/manage_actions.py
import json
import os

ACTIONS_FILE = "actions.json"

def load_actions():
    if not os.path.exists(ACTIONS_FILE):
        return []
    with open(ACTIONS_FILE, "r") as f:
        return json.load(f)

def save_actions(actions):
    with open(ACTIONS_FILE, "w") as f:
        json.dump(actions, f, indent=4)

def prompt_input(prompt_text, default="", note=""):
    if note:
        prompt_text = f"{prompt_text} ({note})"
    user_input = input(f"{prompt_text} [{default}]: ").strip()
    return user_input if user_input else default

def input_sheet_name_with_gid(service, spreadsheet_id):
    """
    Prompt user for a sheet name and get its GID (worksheet ID).
    Retries if not found, or user can leave blank to skip.
    """
    while True:
        sheet_name = prompt_input("Sheet name (leave blank for default)")
        if not sheet_name:
            print("No sheet name provided, leaving sheet_id blank.")
            return "", ""

        try:
            # Open spreadsheet and get worksheet
            spreadsheet = service.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            gid = worksheet.id
            print(f"Found sheet '{sheet_name}' with GID {gid}")
            return sheet_name, gid
        except Exception as e:
            print(f"❌ Sheet '{sheet_name}' not found: {e}")
            retry = prompt_input("Try again? (y/n)", "y").lower()
            if retry != "y":
                print("Skipping sheet selection.")
                return "", ""

def collect_source_values(action, allow_sheet=False):
    """Collect source type, CSV/manual input, and column total."""
    source_type_options = ["csv", "manual"]
    if allow_sheet:
        source_type_options.append("sheet")
    source_type = prompt_input(f"Source type ({'/'.join(source_type_options)})", "manual")
    action["source_type"] = source_type

    if source_type == "csv":
        action["csv_file"] = prompt_input("CSV file name (leave blank if not needed)")
    elif source_type == "sheet":
        action["source_sheet"] = prompt_input("Source sheet name (leave blank for default)")
    else:
        # Manual input
        values = prompt_input("Enter comma-separated values").split(",")
        action["values"] = [v.strip() for v in values if v.strip()]
        action["column_total"] = len(action["values"])
    
    return action


def collect_cell_formats(action, column_total=None):
    """Prompt user for cell formats for each column."""
    if not column_total:
        column_total = int(prompt_input("Total columns", str(action.get("column_total", 1))))
    action["column_total"] = column_total

    cell_formats = []
    for i in range(column_total):
        fmt_type = prompt_input(
            f"Column {i+1} format type (text/number/link/percent/formula/currency/TAGS/date)",
            "text"
        )
        default_val = ""
        if fmt_type in ["link", "formula", "text", "number", "currency", "TAGS", "date"]:
            default_val = prompt_input(f"Column {i+1} default value", "")
        note = prompt_input(f"Column {i+1} note (description for this column)", "")
        cell_formats.append({
            "type": fmt_type,
            "default": default_val,
            "note": note
        })
    action["cell_formats"] = cell_formats
    return action


def handle_append_details(action):
    """Handle extra prompts and structure for append actions."""
    append_mode = prompt_input("Append type (single/multiple)", "single")
    action["append_mode"] = append_mode

    if append_mode == "single":
        action["start_cell"] = prompt_input("Target cell (e.g., A2)", "A1")
        values = prompt_input("Enter comma-separated values").split(",")
        action["values"] = [v.strip() for v in values if v.strip()]
        action["column_total"] = len(action["values"])
        print(f"Captured {action['column_total']} column(s) for single append.")
    else:
        # Multiple rows: CSV/manual/sheet
        action = collect_source_values(action, allow_sheet=True)
        action["start_cell"] = prompt_input("Start cell (e.g., A1, if append just the letter)", "A1")
        action["open_sheet"] = prompt_input("Open sheet before appending? (y/n)", "n").lower() == "y"
        action = collect_cell_formats(action)

    return action

def handle_update_details(action):
    """Handle extra prompts and structure for update actions."""
    action = collect_source_values(action, allow_sheet=False)
    action["target_cell"] = prompt_input("Target cell to update (e.g., B2 or B2:D2)", "A1")
    action["open_sheet"] = prompt_input("Open sheet after update? (y/n)", "n").lower() == "y"
    action = collect_cell_formats(action)
    return action

def create_action(service=None, spreadsheet_id=None):
    """Collect general action configuration, then delegate to type-specific details."""
    action = {}
    action["name"] = prompt_input("Action name")
    action["action"] = prompt_input("Action type (append/update/custom_script/delete)")

    # --- Sheet selection ---
    if service and spreadsheet_id:
        sheet_name, gid = input_sheet_name_with_gid(service, spreadsheet_id)
        action["sheet_name"] = sheet_name
        action["sheet_id"] = gid
    else:
        action["sheet_name"] = prompt_input("Sheet name (leave blank for default)")
        action["sheet_id"] = ""

    # --- Type-specific details ---
    if action["action"] == "append":
        action = handle_append_details(action)
    elif action["action"] == "update":
        action = handle_update_details(action)
    elif action["action"] == "custom_script":
        action["custom_script"] = prompt_input("Custom script file name")

    else:
        # Default generic fields for other action types
        action["start_cell"] = prompt_input("Start cell (e.g., B2)", "A1")
        action["column_total"] = int(prompt_input("Total columns", "1"))

    return action


def delete_action(actions):
    if not actions:
        print("No actions to delete.")
        return actions
    for idx, act in enumerate(actions):
        print(f"{idx}: {act['name']} ({act['action']})")
    sel = int(prompt_input("Select action index to delete", "-1"))
    if 0 <= sel < len(actions):
        removed = actions.pop(sel)
        print(f"Removed action: {removed['name']}")
    else:
        print("Invalid selection.")
    return actions

def main(config, service):
    actions = load_actions()

    while True:
        print("\nManage Actions Menu:")
        print("1. List actions")
        print("2. Create new action")
        print("3. Delete action")
        print("0. Exit")

        choice = prompt_input("Choose option", "0")

        if choice == "1":
            if not actions:
                print("No actions defined yet.")
            else:
                for idx, act in enumerate(actions):
                    print(f"{idx}: {act['name']} ({act['action']})")
        elif choice == "2":
            new_action = create_action(service, config.get("spreadsheet_id"))
            actions.append(new_action)
            save_actions(actions)
            print("Action added successfully.")
        elif choice == "3":
            actions = delete_action(actions)
            save_actions(actions)
        elif choice == "0":
            print("Exiting manage actions.")
            break
        else:
            print("Invalid choice. Try again.")
