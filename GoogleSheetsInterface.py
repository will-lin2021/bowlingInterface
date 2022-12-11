"""

GoogleSheetsInterface
Written By: William Lin

Description:
Interface to Google Sheets using Google API Services

Use of Google API OAuth 2.0 Client credentials from cloud.google.com

"""

from os.path import exists as token_exists
from httplib2.error import ServerNotFoundError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class APIConnectionError(Exception):
    def __init__(self, message="Unable to Connect to Google API Servers"):
        self.message = message


class DataGetError(Exception):
    def __init__(self, message="Unable to Get Data"):
        self.message = message


class DataSetError(Exception):
    def __init__(self, message="Unable to Set Data"):
        self.message = message


class GoogleSheetsInterface:
    # Constructors
    def __init__(self, spreadsheet_id: str, sheet_name: str):
        """
        Google spreadsheet interface using Google's API
        :param spreadsheet_id: id for spreadsheet found from URL
        :param sheet_name: range of sheet in A1 notation
        :raises APIConnectionError: unable to connect to Google API
        """

        # print("API Credential Check")

        creds = None
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        if token_exists(".secrets/token.json"):
            creds = Credentials.from_authorized_user_file(
                ".secrets/token.json",
                scope
            )
        try:
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        ".secrets/credentials.json",
                        scope
                    )
                    creds = flow.run_local_server(port=0)
                with open(".secrets/token.json", 'w') as token:
                    token.write(creds.to_json())
        except ServerNotFoundError as err:
            # print("API Credential Check Failed... exiting...\n")
            raise APIConnectionError(str(err))
        except HttpError as err:
            # print("API Credential Check Failed... exiting...\n")
            raise APIConnectionError(str(err))

        # print("API Credential Check Successful\n")

        service = build(
            "sheets",
            "v4",
            credentials=creds
        )

        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_name
        self.sheet = service.spreadsheets()

        # print("API HTTP Call Check")

        request = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range
        )

        try:
            request.execute()
        except ServerNotFoundError as err:
            # print("API HTTP Call Check Failed... exiting...\n")
            raise APIConnectionError(str(err))
        except HttpError as err:
            # print("API HTTP Call Check Failed... exiting...\n")
            raise APIConnectionError(str(err))

        # print("API HTTP Call Check Successful\n")

    # Getters
    def get_data(self, end_row: int = 0, end_col: int = 0, start_row: int = 1, start_col: int = 1) -> list:
        """
        Gets data for a given range in sheet
        :param int end_row: end row index for data
        :param end_col: end column index for data
        :param start_row: start row index for data
        :param start_col: start column index for data
        :return: 2D list containing sheet elements
        :raises InvalidRangeException: inputted range is not valid
        :raises APIConnectionError: unable to connect to Google API
        """

        if end_row and end_row < start_row:
            raise DataGetError(f"Invalid Row Bounds: {start_row} - {end_row}")
        if end_col and end_col < start_col:
            raise DataGetError(f"Invalid Column Bounds: {start_col} - {end_col}")

        if not end_row and not end_col:  # no end bounds provided
            sheet_range = self.sheet_range
        elif not end_row:  # no row end bound provided
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, self.get_num_row(), end_col)
        elif not end_col:  # no col end bound provided
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, end_row, self.get_num_col())
        else:  # all bounds provided
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, end_row, end_col)

        request = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range
        )

        try:
            result = request.execute()

            values = result.get(
                "values",
                []
            )

            return values
        except ServerNotFoundError as err:
            raise APIConnectionError(f"{str(err)}")
        except HttpError as err:
            raise DataGetError(f"{str(err)}")

    def get_cell(self, row: int, col: int) -> str:
        """
        Gets element from sheet at given row and column index
        :param row: row index
        :param col: column index
        :return: element in given row and column index; returns <code>""</code> if no element is found
        :raises DataGetError: input row or col indices is outside of sheet range
        """

        if row < 1 or self.get_num_row() < row:
            raise DataGetError(f"Input Row outside Range: {row} -> (1, {self.get_num_row()}")
        if col < 1 or self.get_num_col() < col:
            raise DataGetError(f"Input Column outside Range: {col} -> (1, {self.get_num_col()}")

        try:
            data = self.get_data(row, col, row, col)
            if not data:
                return ""

            return data[0][0]
        except APIConnectionError as err:
            raise DataGetError(f"Unable to Get Data from Cell: {err}")

    def get_val_index(self, val: str, col_or_row_num: int, colSearch: bool = False) -> int:
        """
        Gets row or column index for given value in column or row
        :param val: search value
        :param col_or_row_num: index of row or column
        :param colSearch: True to perform column search, else row search
        :return: index location of value; returns <code>0</code>
        """

        if colSearch:  # Searching column
            n_rows = self.get_num_row()

            try:
                data = self.get_data(n_rows, col_or_row_num, 1, col_or_row_num)
                if not data:
                    return 0

                for r, row in enumerate(data, start=1):
                    if row and row[0] == val:
                        return r

                return 0
            except APIConnectionError as err:
                raise DataGetError(str(err))
        else:  # Searching row
            n_cols = self.get_num_col()

            try:
                data = self.get_data(col_or_row_num, n_cols, col_or_row_num, 1)
                if not data:
                    return 0

                for c, col in enumerate(data[0], start=1):
                    if col and col[0] == val:
                        return c

                return 0
            except APIConnectionError as err:
                raise DataGetError(str(err))

    def get_num_row(self) -> int:
        """
        Get total number of row in sheet
        :return: number of rows in sheet
        """

        try:
            data = self.get_data()
            if not data:
                return 0

            return len(data)
        except APIConnectionError as err:
            print(err)
            return 0

    def get_num_col(self) -> int:
        """
        Get total number of columns in sheet
        :return: number of columns in sheet
        """

        try:
            data = self.get_data()
            if not data:
                return 0

            return len(max(data, key=len))
        except APIConnectionError as err:
            print(err)
            return 0

    # Setters
    def set_cell(self, row: int, col: int, val: str) -> bool:
        """
        Set a value to a given indices
        :param row: row index
        :param col: column index
        :param val: value to set
        :return: cell set success
        """

        values = [
            [val]
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range + GoogleSheetsInterface.get_cell_range(row, col, row, col),
            valueInputOption="USER_ENTERED",
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError:
            return False

    def set_row(self, row: int, col: int, vals: list) -> bool:
        """
        Set row with elements of list starting at given indices
        :param row: starting row index
        :param col: starting column index
        :param vals: list of elements to set
        :return: row set success
        """

        values = [
            vals
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range + GoogleSheetsInterface.get_cell_range(row, col, row, col + len(vals) - 1),
            valueInputOption="USER_ENTERED",
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError:
            return False

    def set_col(self, row: int, col: int, vals: list) -> bool:
        """
        Set col with elements of list starting at given indices
        :param row: starting row index
        :param col: starting col index
        :param vals: list of elements to set
        :return: if unable to set, returns False
        """

        values = [[element] for element in vals]
        body = {
            "values": values
        }

        request = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range + GoogleSheetsInterface.get_cell_range(row, col, row + len(vals) - 1, col),
            valueInputOption="USER_ENTERED",
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError:
            return False

    # Functions
    def add_row(self, row: int) -> int:
        """
        Add row to sheet at given index
        :param row: row index
        :return: index of new row; if unable to add row, returns 0
        :raises OutOfRangeException: index is out of the add-able range
        """

        n_rows = self.get_num_row()
        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return 0

        if row == n_rows + 1:
            body = {
                "requests": [
                    {
                        "appendDimension": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "length": 1
                        }
                    }
                ]
            }
        elif 0 < row <= n_rows:
            body = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "ROWS",
                                "startIndex": row - 1,
                                "endIndex": row
                            }
                        }
                    }
                ]
            }
        else:
            raise DataSetError(str(row))

        request = self.sheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        )

        try:
            result = request.execute()

            return row if result else 0
        except HttpError:
            return 0

    def add_col(self, col: int) -> int:
        """
        Add column to sheet at given index
        :param col: column index
        :return: index of new column; if unable add column, returns 0
        :raises OutOfRangeException: index is out of the add-able range
        """

        n_cols = self.get_num_col()
        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return 0

        if col == n_cols + 1:
            body = {
                "requests": [
                    {
                        "appendDimension": {
                            "sheetId": self.__get_sheet_id(),
                            "dimension": "COLUMNS",
                            "length": 1
                        }
                    }
                ]
            }
        elif 0 < col <= n_cols:
            body = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": self.__get_sheet_id(),
                                "dimension": "COLUMNS",
                                "startIndex": col - 1,
                                "endIndex": col
                            }
                        }
                    }
                ]
            }
        else:
            raise DataSetError(str(col))

        request = self.sheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        )

        try:
            result = request.execute()

            return col if result else 0
        except HttpError:
            return 0

    def resize_row(self, row: int, size: int) -> bool:
        """
        Resizes row at given index
        :param row: row index
        :param size: new size of row (0 to auto-resize)
        :return: bool - success; returns <code>False</code> if resizing was not successful
        """

        n_rows = self.get_num_row()
        if row < 1 or n_rows < row:
            raise DataGetError(str(row))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        if size:
            body = {
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "ROWS",
                                "startIndex": row - 1,
                                "endIndex": row
                            },
                            "properties": {
                                "pixelSize": size
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }
        else:
            body = {
                "requests": [
                    {
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": sheet_id,
                                "dimension": "ROWS",
                                "startIndex": row - 1,
                                "endIndex": row
                            }
                        }
                    }
                ]
            }

        request = self.sheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError as err:
            print(err)
            return False

    def resize_col(self, col: int, size: int) -> bool:
        """
        Resizes column at given column index
        :param col: column index
        :param size: new size of row (0 to autoresize)
        :return: bool - success; returns <code>False</code> if resizing was not successful
        """

        n_cols = self.get_num_col()
        if col < 1 or n_cols < col:
            raise DataGetError(str(col))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        if size:
            body = {
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": col - 1,
                                "endIndex": col
                            },
                            "properties": {
                                "pixelSize": size
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }
        else:
            body = {
                "requests": [
                    {
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": col - 1,
                                "endIndex": col
                            }
                        }
                    }
                ]
            }

        request = self.sheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError as err:
            print(err)
            return False

    def delete_row(self, row: int) -> list:
        """
        Deletes row at given row index
        :param row: row index
        :return: boolean - deletion success
        """

        # TODO
        return [row]

    def delete_col(self, col: int) -> list:
        """
        Deletes row at given column index
        :param col: column index
        :return: boolean - deletion success
        """

        # TODO
        return [col]

    def move_row(self, row_src: int, row_dest: int) -> None:
        """
        Moves row from input indices
        :param row_src: row index of source
        :param row_dest: row index of destination
        :return: None
        """

        # TODO
        return

    def move_col(self, col_src: int, col_dest: int) -> None:
        """
        Moves column from input indices
        :param col_src: column index of source
        :param col_dest: column index of destination
        :return: None
        """

        # TODO
        return

    def print(self, end_row: int, end_col: int,
              start_row: int = 1, start_col: int = 1) -> bool:
        """
        Prints sheet within given row and column bounds auto centering the text
        :param end_row: end row index (0: to print entire sheet)
        :param end_col: end column index (0: to print entire sheet)
        :param start_row: start row index (default: 1)
        :param start_col: start column index (default: 1)
        :return: boolean - contains data
        """

        try:
            data = self.get_data(end_row, end_col, start_row, start_col)
            if not data:
                return False

            max_len = 0
            for row in data:
                if row:
                    row_max = len(max(row, key=len))
                    max_len = max(max_len, row_max)

            for row in data:
                for col in row:
                    print(col.center(max_len), end=" ")
                print()

            return True
        except APIConnectionError as err:
            print(err)
            return False

    def format_print(self, end_row: int, end_col: int,
                     start_row: int = 1, start_col: int = 1,
                     col_spacing: list = None, col_r_just: list = None) -> bool:
        """
        Prints sheet within given row and column bounds with column spacing and justification
        :param end_row: end row index
        :param end_col: end column index
        :param start_row: start row index
        :param start_col: end column index
        :param col_spacing: list of integer values for the spacing of each column
        :param col_r_just: list of boolean values for whether to right justify text
        :return: None
        """

        if not col_spacing and not col_r_just:
            return True if self.print(end_row, end_col, start_row, start_col) else False

        try:
            data = self.get_data(end_row, end_col, start_row, start_col)
            if not data:
                return False

            if not col_spacing:  # no spacing specified
                for row in data:
                    for n_col, col in enumerate(row):
                        if not col_r_just[n_col]:
                            print(col.ljust(len(col)), end=" ")
                        else:
                            print(col.rjust(len(col)), end=" ")
                    print()
            elif not col_r_just:  # no justification specified
                for row in data:
                    for n_col, col in enumerate(row):
                        if col_spacing[n_col] == -1:
                            print("|", end=" ")
                        else:
                            print(col.ljust(col_spacing[n_col]), end=" ")
                    print()
            else:
                for row in data:
                    for n_col, col in enumerate(row):
                        if col_r_just[n_col]:  # right just
                            if col_spacing[n_col] == -1:
                                print("|", end=" ")
                            else:
                                print(col.rjust(col_spacing[n_col]), end=" ")
                        else:  # left just
                            if col_spacing[n_col] == -1:
                                print("|", end=" ")
                            else:
                                print(col.ljust(col_spacing[n_col]), end=" ")
                    print()

                return True
        except APIConnectionError as err:
            print(err)
            return False

    # Sheet Backend Methods
    def __get_sheet_id(self) -> int:
        """
        Get sheet ID of sheet initialized
        :return: int - sheet ID
        """
        request = self.sheet.get(
            spreadsheetId=self.spreadsheet_id
        )

        try:
            result = request.execute()

            for _sheet in result["sheets"]:
                if _sheet["properties"]["title"] == self.sheet_range:
                    return _sheet["properties"]["sheetId"]
            return -1
        except HttpError:
            print("Unable to get Sheet ID")
            return -1

    # Helpers
    @staticmethod
    def get_abc_col(col: int) -> str:
        """
        Get the letter equivalent of an integer
        :param col: column index
        :return: column index as a spreadsheet column letter
        """

        def get_letter(num: int) -> str:
            return chr(65 + num)

        output = ""
        a = col
        while a > 0:
            b = (a - 1) % 26
            a = (a - 1) // 26
            output = get_letter(b) + output
        return output

    @staticmethod
    def get_cell_range(start_row: int, start_col: int, end_row: int, end_col: int) -> str:
        """
        Get the A1 representation of a sheet range
        :param start_row: start row index
        :param start_col: start column index
        :param end_row: end row index
        :param end_col: end column index
        :return: sheet range in A1 format as a string
        """
        return "!" + \
            GoogleSheetsInterface.get_abc_col(start_col) + str(start_row) + ":" + \
            GoogleSheetsInterface.get_abc_col(end_col) + str(end_row)


def main(args):
    try:
        instance = GoogleSheetsInterface("1_FMEwtAsS_yEpspGJYuWvbnx-9QVAfdQimqE31W7pME", "TestSheet")
    except APIConnectionError as err:
        print(err)
        return 1

    print(instance.resize_col(1, 25))


if __name__ == "__main__":
    from sys import argv

    main(argv)
