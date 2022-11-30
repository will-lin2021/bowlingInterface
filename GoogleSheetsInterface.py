from os.path import exists as token_exists

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2.error import ServerNotFoundError


class GoogleSheetsInterface:
    # Constructors
    def __init__(self, sheet_id: str, sheet_range: str):
        print("Checking for API credentials...")
        creds = None
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        if token_exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json",
                scope
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    scope
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", 'w') as token:
                token.write(creds.to_json())
        print("Checking for API credentials successful")
        print()
        print("Getting spreadsheet resources...")
        try:
            service = build(
                "sheets",
                "v4",
                credentials=creds
            )

            self.sheet_id = sheet_id
            self.sheet_range = sheet_range
            self.sheet = service.spreadsheets()

            print("Getting spreadsheet resources successful")
            print()
            print("Testing Http Calls...")
            self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range
            ).execute()
        except HttpError as err:
            print("Testing Http Calls Failed")
            print("Check for valid Sheet ID and/or Sheet Range")
            print("Traceback:")
            print(err)
            self.sheet = None
            return
        except ServerNotFoundError as err:
            print("Testing Http Calls Failed")
            print("Check for valid internet connection")
            print("Traceback:")
            print(err)
            self.sheet = None
            return
        print("Testing Http Calls Successful\n")

    # Getters
    def get_data(self, start_row: int = None, start_col: int = None, end_row: int = None, end_col: int = None):
        if not start_row and not start_col and not end_row and not end_col:
            sheet_range = self.sheet_range
        else:
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, end_row, end_col)

        result = self.sheet.values().get(
            spreadsheetId=self.sheet_id,
            range=sheet_range
        ).execute()

        values = result.get(
            "values",
            []
        )

        return None if not values else values

    def get_cell(self, row: int, col: int) -> str:
        data = self.get_data(row, col, row, col)
        if not data:
            return "Null"

        return data[0][0]

    def get_val(self, val: str, col_or_row_num: int, isCol: bool = False) -> (int, int, str):  # TODO: create get_val method
        if isCol:  # Searching column
            n_rows = self.get_num_row()
            data = self.get_data(1, col_or_row_num, n_rows, col_or_row_num)
            if not data:
                return -1, -1, "Null"

            for r, row in enumerate(data, start=1):
                if row and row[0] == val:
                    return r, col_or_row_num, val
        else:  # Searching row
            n_cols = self.get_num_col()
            data = self.get_data(col_or_row_num, 1, col_or_row_num, n_cols)
            if not data:
                return -1, -1, "Null"

            for c, col in enumerate(data[0], start=1):
                if col == val:
                    return col_or_row_num, c, val
        return -1, -1, val

    def get_num_col(self) -> int:
        data = self.get_data()
        if not data:
            return -1

        return len(data[0])

    def get_num_row(self) -> int:
        data = self.get_data()
        if not data:
            return -1

        return len(data)

    # Setters
    def set_cell(self, row: int, col: int, val: str) -> bool:
        data = self.get_data(row, col, row, col)
        if not data:
            return False

        values = [
            [val]
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().update(
            spreadsheetId=self.sheet_id,
            range=self.sheet_range + GoogleSheetsInterface.get_cell_range(row, col, row, col),
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return True
    
    # Functions
    def add_row(self, row: int) -> int:  # TODO: creates a new row at the given row, returns the row number
        body = {
            "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": "0",
                                "dimension": "ROWS",
                                "startIndex": row-1,
                                "endIndex": row
                            }
                        }
                    }
                ]
        }

        request = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id,
            body=body
        ).execute()

        return row

    def add_col(self, col: int) -> int:  # TODO: creates a new col at the given col, returns the col number (or letter)
        body = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": "0",
                            "dimension": "COLUMNS",
                            "startIndex": col - 1,
                            "endIndex": col
                        }
                    }
                }
            ]
        }

        request = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id,
            body=body
        ).execute()

        return col

    def print(self, start_row: int, start_col: int,
              end_col: int, end_row: int) -> None:
        data = self.get_data(start_row, start_col, end_row, end_col)

        if not data:
            return

        max_len = 0
        for row in data:
            row_max = len(max(row, key=len))
            if row_max > max_len:
                max_len = row_max

        for row in data:
            for col in row:
                print(col.center(max_len), end=" ")
            print()

    def format_print(self, start_row: int, start_col: int, format_spacing):
        # TODO: create a function that can print with spacing added, specified in input list
        return

    # Helpers
    @staticmethod
    def get_abc_col(col: int) -> str:
        def get_letter(num: int) -> str:
            return chr(65+num)
        output = ""
        a = col
        while a > 0:
            b = (a - 1) % 26
            a = (a - 1) // 26
            output = get_letter(b) + output
        return output

    @staticmethod
    def get_cell_range(start_row: int, start_col: int, end_row: int, end_col: int) -> str:
        return "!" +\
               GoogleSheetsInterface.get_abc_col(start_col) + str(start_row) + ":" +\
               GoogleSheetsInterface.get_abc_col(end_col) + str(end_row)


def main(args):
    instance = GoogleSheetsInterface("1_FMEwtAsS_yEpspGJYuWvbnx-9QVAfdQimqE31W7pME", "TestSheet")
    print(instance.get_cell(1, 1))


if __name__ == "__main__":
    from sys import argv
    main(argv)
