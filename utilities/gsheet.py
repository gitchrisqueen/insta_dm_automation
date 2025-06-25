import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = 'config/credentials.json'


def get_gspread_client():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
    return gspread.authorize(credentials)


def get_sheet(spreadsheet_id: str, sheet_name: str = None):
    """
    Returns a gspread worksheet object.
    If sheet_name is None, it defaults to the first sheet in the spreadsheet.
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    if sheet_name:
        return spreadsheet.worksheet(sheet_name)
    else:
        return spreadsheet.sheet1  # default to first sheet


def get_unprocessed_rows(sheet):
    """
    Returns list of rows with data format: (row_index, Profile Url, message)
    Skips header row (row 1) and rows where status column is not filled.
    Column indexes are determined by header names.
    """
    data = sheet.get_all_values()
    if not data or len(data) < 2:
        return []

    header = data[0]
    try:
        profile_url_idx = header.index("Profile Url")
        message_idx = header.index("message")
        status_idx = header.index("status")
    except ValueError as e:
        raise ValueError(f"Required column missing: {e}")

    rows = []
    for idx, row in enumerate(data[1:], start=2):
        if len(row) <= profile_url_idx or not row[profile_url_idx].strip():
            continue
        status = row[status_idx] if len(row) > status_idx else ''
        if not status.strip():
            profile_url = row[profile_url_idx]
            message = row[message_idx] if len(row) > message_idx else ''
            rows.append((idx, profile_url, message))
    return rows

def mark_status(sheet, row_index, status: str):
    header = sheet.row_values(1)
    try:
        status_idx = header.index("status") + 1  # gspread uses 1-based indexing
    except ValueError:
        raise ValueError("Required column 'status' not found in header")
    sheet.update_cell(row_index, status_idx, status)


# Optional CLI test
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Google Sheet Access")
    parser.add_argument("spreadsheet_id", help="The ID of the Google Spreadsheet")
    parser.add_argument("--sheet_name", help="Optional sheet name (default is first sheet)")
    args = parser.parse_args()

    sheet = get_sheet(args.spreadsheet_id, args.sheet_name)
    rows = get_unprocessed_rows(sheet)
    for idx, url, msg in rows:
        print(f"Row {idx}: {url} | Message: {msg}")
        mark_status(sheet, idx, "✅ Tested")
