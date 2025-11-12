# main.py
import json
import gspread
from google.oauth2.service_account import Credentials
from src import manage_actions
from src import append  # we'll create this next


def load_config():
    """Load configuration from config.json"""
    with open("config.json", "r") as f:
        return json.load(f)


def load_actions():
    """Load saved actions from actions.json"""
    try:
        with open("actions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ actions.json not found — no actions available.")
        return []
    except json.JSONDecodeError:
        print("⚠️ Failed to parse actions.json — check file format.")
        return []


def init_gspread_client(credentials_file):
    """Initialize gspread client using service account credentials"""
    try:
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"❌ Failed to initialize gspread client: {e}")
        return None


def main():
    config = load_config()
    client = init_gspread_client(config.get("credentials_file"))

    if not client:
        print("Google Sheets client not available. Exiting.")
        return

    spreadsheet_id = config.get("spreadsheet_id")
    if not spreadsheet_id:
        print("No 'spreadsheet_id' found in config.json. Exiting.")
        return

    spreadsheet = client.open_by_key(spreadsheet_id)
    print(f"Currently managing '{spreadsheet.title}'")
    version = config.get("version", "unknown")
    while True:
        # === Load actions each loop in case they were updated ===
        actions = load_actions()

        print(f"\n=== G-Sheet Manager v{version} ===")
        print("\nAvailable actions:")
        print("0. Manage actions (create/edit/delete)")
        for i, action in enumerate(actions, start=1):
            print(f"{i}. {action['name']} ({action['action']})")
        print("Q. Quit program")

        choice = input("\nChoose an option: ").strip().lower()

        if choice == "q":
            print("Exiting program.")
            break

        # Manage actions
        if choice == "0":
            manage_actions.main(config, client)
            continue

        # Run selected action
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(actions):
                print("❌ Invalid action number.")
                continue
            selected_action = actions[index]
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'Q' to quit.")
            continue

        print(f"\n▶ Running action: {selected_action['name']} ({selected_action['action']})")

        action_type = selected_action["action"]
        if action_type == "append":
            append.main(client, spreadsheet_id, selected_action, config)
        elif action_type == "update":
            from src import update
            update.main(client, spreadsheet_id, selected_action, config)
        elif action_type == "custom_script":
            import importlib.util
            import os

            script_file = selected_action.get("custom_script")
            if not script_file:
                print("❌ No custom script specified in action.")
                continue

            script_path = os.path.join("custom_script", script_file)
            if not os.path.exists(script_path):
                print(f"❌ Custom script not found: {script_path}")
                continue

            spec = importlib.util.spec_from_file_location("custom_script", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "main"):
                print(f"▶ Running custom script: {script_file}")
                module.main()
            else:
                print(f"❌ Script {script_file} does not have a main() function.")

        print("\n✅ Action completed. Returning to main menu...\n")

if __name__ == "__main__":
    main()
