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
    @dispatch()
    def get_data(self):
        result = self.sheet.values().get(
            spreadsheetId=self.sheet_id,
            range=self.sheet_range
        ).execute()

        values = result.get(
            "values",
            []
        )

        if not values:
            return None
        else:
            return values

    @dispatch(int, int, int, int)
    def get_data(self, start_col: int, start_row: int, end_col: int, end_row: int):
        result = self.sheet.values().get(
            spreadsheetId=self.sheet_id,
            range=self.sheet_range + GoogleSheetsInterface.get_cell_range(start_col, start_row, end_col, end_row)
        ).execute()

        values = result.get(
            "values",
            []
        )

        return None if not values else values

    def get_cell(self, row: int, col: int) -> str:  # TODO: create get method for cell
        data = self.get_data()

        return

    def get_val(self, val: str, col_or_row: str, isCol: bool = False) -> (int, str):  # TODO: create get_val method
        if isCol:  # Searching column
            return -1, "Col Search"
        else:  # Searching row
            return -1, "Row Search"

    def get_last_col(self) -> int:
        data = self.get_data()
        c = 0
        for row in data:
            for col_num, col in enumerate(row, start=1):
                c = max(c, col_num)
        return c

    def get_last_row(self) -> int:  # TODO: gets row number of last filled row
        data = self.get_data()
        r = 0
        for r_num, row in enumerate(data, start=1):
            r = r_num
        return r

    # Setters
    def set_cell(self, val: str, row: int, col: int) -> None:  # TODO: create set method for cell
        return None
    
    # Functions
    def find_empty_row(self) -> int:  # TODO: gets row number of the first empty row
        data = self.get_data()
        r = 0
        for r, row in enumerate(data, start=1):
            continue
        return r + 1

    def add_row(self, row: int) -> int:  # TODO: creates a new row at the given row, returns the row number
        values = [
            ["temp"]
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().batchUpdate(
            spreadsheetId=self.sheet_id,
            body={
                "insertRange": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 2,
                        "endRowIndex": 3,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    },
                    "shiftDimension": "ROWS"
                }
            }
        )
        request.execute()

        request = self.sheet.values().append(
            spreadsheetId=self.sheet_id,
            range=self.sheet_range + self.get_cell_range(1, row, 1, row),
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        )
        request.execute()

        return row

    def add_col(self, col: int) -> int:  # TODO: creates a new col at the given col, returns the col number (or letter)
        return -1

    def print(self, start_col: int, start_row: int,
              end_col: int, end_row: int) -> None:
        data = self.get_data(start_col, start_row, end_col, end_row)

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
    def get_cell_range(start_col: int, start_row: int, end_col: int, end_row: int) -> str:
        return "!" +\
               GoogleSheetsInterface.get_abc_col(start_col) + str(start_row) + ":" +\
               GoogleSheetsInterface.get_abc_col(end_col) + str(end_row)


def main(args):
    instance = GoogleSheetsInterface("1_FMEwtAsS_yEpspGJYuWvbnx-9QVAfdQimqE31W7pME", "Sheet1")
    instance.add_row(5)


if __name__ == "__main__":
    from sys import argv
    main(argv)
