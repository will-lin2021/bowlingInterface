"""

StorageInterface.py
Written By: William Lin

Description:
Interface to Storage Interfaces, cloud-based (Google Sheets) and locally-based (mariaDb)

Uses:
    - Google API OAuth 2.0 Client credentials from cloud.google.com
    - MariaDB

"""

import csv
import mariadb
from os.path import exists as token_exists
from httplib2.error import ServerNotFoundError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetInterface:
    def __init__(self, spreadsheet_id: str, sheet_name: str):
        self.valid = True
        creds = None
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        if token_exists(".secrets/token.json"):
            creds = Credentials.from_authorized_user_file(
                ".secrets/token.json",
                scope
            )

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

        service = build(
            "sheets",
            "v4",
            credentials=creds
        )

        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_name
        self.sheet = service.spreadsheets()

        request = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range
        )

        try:
            request.execute()
        except Exception as err:
            self.valid = False
            self.err = err

    def add_row(self):
        return

    def get_row(self):
        return

    def set_row(self):
        return

    def del_row(self):
        return

    def add_col(self):
        return

    def get_col(self):
        return

    def set_col(self):
        return

    def del_col(self):
        return

    def import_csv(self):
        return


class GoogleSheetsInterface:
    # TODO: Simplify Interface
    # TODO: Limit to Add, Get, Set, Delete Row and Col

    # Constructor
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
        Gets data for a given range in sheet. Enter `0` for end indices to select rest of data
        :param int end_row: end row index for data
        :param end_col: end column index for data
        :param start_row: start row index for data
        :param start_col: start column index for data
        :return: 2D list containing sheet elements
        :raises InvalidRangeException: inputted range is not valid
        :raises APIConnectionError: unable to connect to Google API
        """

        # Check for valid bound
        if end_row and end_row < start_row:
            raise DataGetError(f"Invalid Row Bounds: {start_row} - {end_row}")
        if end_col and end_col < start_col:
            raise DataGetError(f"Invalid Column Bounds: {start_col} - {end_col}")

        # Get data range
        if not end_row and not end_col and start_row == 1 and start_col == 1:  # get all data
            sheet_range = self.sheet_range
        elif not end_row and not end_col:  # get data after provided start row and column bounds (inclusive)
            sheet_range = self.sheet_range \
                          + self.get_cell_range(start_row, start_col, self.get_num_row(), self.get_num_col())
        elif not end_row:  # get all data between two column bounds (inclusive)
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, self.get_num_row(), end_col)
        elif not end_col:  # get data between two row bounds (inclusive)
            sheet_range = self.sheet_range + self.get_cell_range(start_row, start_col, end_row, self.get_num_col())
        else:  # get data between row and column bounds (inclusive)
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

        # Check for valid bound
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

    def get_value_index(self, val: str, col_or_row_num: int, col_search: bool = False) -> int:
        """
        Gets row or column index for given value in column or row
        :param val: search value
        :param col_or_row_num: index of row or column
        :param col_search: True to perform column search, else row search
        :return: index location of value; returns <code>0</code>
        """

        if col_search:  # Searching column
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
        Get total number of row in sheet (including empty rows)
        :return: number of rows in sheet
        """

        request = self.sheet.get(
            spreadsheetId=self.spreadsheet_id,
            ranges=self.sheet_range
        )

        try:
            result = request.execute()

            return result["sheets"][0]["properties"]["gridProperties"]["rowCount"]
        except APIConnectionError as err:
            print(err)
            return 0

    def get_num_col(self) -> int:
        """
        Get total number of columns in sheet (including empty columns)
        :return: number of columns in sheet
        """

        request = self.sheet.get(
            spreadsheetId=self.spreadsheet_id,
            ranges=self.sheet_range
        )

        try:
            result = request.execute()

            return result["sheets"][0]["properties"]["gridProperties"]["columnCount"]
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
        except HttpError as err:
            print(err)
            return False

    def append_cells(self, data: list):
        body = {
            "majorDimension": "ROWS",
            "values": data
        }

        request = self.sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        )

        try:
            result = request.execute()

            return True if result else False
        except HttpError as err:
            print(err)
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
    def add_row(self, row: int) -> bool:
        """
        Add row to sheet at given index
        :param row: row number
        :return: index of new row; if unable to add row, returns 0
        :raises OutOfRangeException: index is out of the add-able range
        """

        n_rows = self.get_num_row()
        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

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

            return True if result else False
        except HttpError as err:
            print(err)
            return True

    def add_col(self, col: int) -> bool:
        """
        Add column to sheet at given index
        :param col: column number
        :return: index of new column; if unable add column, returns 0
        :raises OutOfRangeException: index is out of the add-able range
        """

        n_cols = self.get_num_col()
        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

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

            return True if result else False
        except HttpError as err:
            print(err)
            return False

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
        Resizes column at given index
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

    def delete_row(self, row: int) -> bool:
        """
        Deletes row at given index
        :param row: row index
        :return: boolean - deletion success
        """

        n_rows = self.get_num_row()
        if row < 1 or n_rows < row:
            raise DataGetError(str(row))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        body = {
            "requests": [
                {
                    "deleteDimension": {
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

    def delete_col(self, col: int) -> bool:
        """
        Deletes row at given index
        :param col: column index
        :return: boolean - deletion success
        """

        n_cols = self.get_num_col()
        if col < 1 or n_cols < col:
            raise DataGetError(str(col))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
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

    def move_row(self, row_src: int, row_dest: int) -> bool:
        """
        Moves row from input indices
        :param row_src: row index of source
        :param row_dest: row index of destination
        :return: None
        """

        n_rows = self.get_num_row()
        if row_src < 1 or n_rows < row_src:
            raise DataGetError(str(row_src))
        if row_dest < 1 or n_rows < row_dest:
            raise DataGetError(str(row_dest))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        body = {
            "requests": [
                {
                    "moveDimension": {
                        "source": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": row_src - 1,
                            "endIndex": row_src
                        },
                        "destinationIndex": row_dest
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

    def move_col(self, col_src: int, col_dest: int) -> bool:
        """
        Moves column from input indices
        :param col_src: column index of source
        :param col_dest: column index of destination
        :return: None
        """

        n_cols = self.get_num_col()
        if col_src < 1 or n_cols < col_src:
            raise DataGetError(str(col_src))
        if col_dest < 1 or n_cols < col_dest:
            raise DataGetError(str(col_dest))

        sheet_id = self.__get_sheet_id()
        if sheet_id < 0:
            return False

        body = {
            "requests": [
                {
                    "moveDimension": {
                        "source": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": col_src - 1,
                            "endIndex": col_src
                        },
                        "destinationIndex": col_dest
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

    def import_csv(self, filename: str, filepath: str = None, header: bool = True):
        if filepath:
            filepath = filepath + "/" + filename

        with open(filepath, newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            entries = []
            for row in csv_reader:
                if not header:
                    header = True
                    continue
                entries.append(row)

            self.append_cells(entries)

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
            spreadsheetId=self.spreadsheet_id,
            ranges=self.sheet_range
        )

        try:
            result = request.execute()

            return result["sheets"][0]["properties"]["sheetId"]
        except HttpError:
            print("Unable to get Sheet ID")
            return -1

    def get_sheet_id_test(self):
        return self.__get_sheet_id()

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


class MariaDBInterface:
    # Constructor
    def __init__(self, user: str, password: str, database: str):
        self.valid = True

        try:
            self.conn = mariadb.connect(
                user=user,
                password=password,
                host="localhost",
                database=database
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as err:
            self.valid = False
            self.err = err

    # Basic Functions
    def add_row(self, table: str, target_keys: tuple, target_values: tuple):
        if len(target_keys) != len(target_values):
            return None

        target_keys, target_values = self.__values_str(target_keys, target_values)

        self.cursor.execute(
            f"INSERT INTO {table} {target_keys} VALUES {target_values}"
        )
        self.conn.commit()

    def get_row(self, table: str, search_keys: tuple = None, search_values: tuple = None,
                sort_keys: tuple = None, sort_order: tuple = None, num_rows: int = 25):
        if search_keys and search_values and len(search_keys) != len(search_values):
            return None

        if search_keys and search_values and sort_keys:  # get data with search and ordering
            processed_search = self.__where_str(search_keys, search_values)
            processed_sort_keys = self.__orderby_str(sort_keys, sort_order)

            self.cursor.execute(
                f"SELECT * FROM {table} WHERE {processed_search} "
                f"ORDER BY {processed_sort_keys} LIMIT {num_rows}"
            )
        elif not search_keys and not search_values and sort_keys:  # get data with ordering
            processed_sort_keys = self.__orderby_str(sort_keys, sort_order)

            self.cursor.execute(
                f"SELECT * FROM {table} ORDER BY {processed_sort_keys} LIMIT {num_rows}"
            )
        elif search_keys and search_values:  # get data with search
            processed_search = self.__where_str(search_keys, search_values)

            self.cursor.execute(
                f"SELECT * FROM {table} WHERE {processed_search} LIMIT {num_rows}"
            )
        else:  # get all data
            self.cursor.execute(
                f"SELECT * FROM {table} LIMIT {num_rows}"
            )
        return list(self.cursor)

    def set_row(self, table: str, target_keys: tuple, target_values: tuple,
                search_keys: tuple, search_values: tuple, limit: int = 1):
        if len(target_keys) != len(target_values) or len(search_keys) != len(search_values):
            return None

        processed_input = self.__set_str(target_keys, target_values)
        processed_search = self.__where_str(search_keys, search_values)

        self.cursor.execute(
            f"UPDATE {table} SET {processed_input} WHERE {processed_search} LIMIT {limit}"
        )
        self.conn.commit()

    def del_row(self, table: str, target_keys: tuple, target_values: tuple, limit: int = 1):
        if len(target_keys) != len(target_values):
            return None

        processed_search = self.__where_str(target_keys, target_values)

        self.cursor.execute(
            f"DELETE FROM {table} WHERE {processed_search} LIMIT {limit}"
        )
        self.conn.commit()

    # Advanced Functions (requires confirmation)
    def purge_table(self, table: str):
        self.cursor.execute(
            f"DELETE FROM {table}"
        )
        self.conn.commit()

    def add_col(self, table: str, column_name: str, column_type: str):
        self.cursor.execute(
            f"ALTER TABLE {table} ADD {column_name} {column_type}"
        )
        self.conn.commit()

    def set_col(self, table: str, column_name: str, new_type: str):
        self.cursor.execute(
            f"ALTER TABLE {table} MODIFY {column_name} {new_type}"
        )
        self.conn.commit()

    def del_col(self, table: str, column_name: str):
        self.cursor.execute(
            f"ALTER TABLE {table} DROP COLUMN {column_name}"
        )
        self.conn.commit()

    # Helper Functions
    @staticmethod
    def isdate(inp: str) -> bool:
        from dateutil import parser
        try:
            parser.parse(
                timestr=inp,
                parserinfo=parser.parserinfo(False, True)
            )
            return True
        except ValueError:
            print("not date")
            return False
        except TypeError:
            print("not date")
            return False

    @staticmethod
    def __values_str(keys: tuple, values: tuple[str]) -> (str, str):
        output_key = ""
        output_data = ""
        for i, key in enumerate(keys):
            if len(keys) == 1:
                output_key += f"({key})"
                break
            elif i == 0:
                output_key += "("

            if i == len(keys) - 1:
                output_key += f"{key})"
            else:
                output_key += f"{key}, "

        for i, value in enumerate(values):
            if len(values) == 1:
                if isinstance(value, str):
                    output_data += f"('{value}')"
                else:
                    output_data += f"{value}"
                break
            elif i == 0:
                output_data += "("

            if i == len(values) - 1:
                if isinstance(value, str):
                    output_data += f"'{value}')"
                else:
                    output_data += f"{value})"
            else:
                if isinstance(value, str):
                    output_data += f"'{value}', "
                else:
                    output_data += f"{value}, "
        return output_key, output_data

    @staticmethod
    def __where_str(keys: tuple, values: tuple) -> str:
        output = ""
        for i, (key, value) in enumerate(zip(keys, values)):
            if i == len(keys) - 1:
                if value is None:
                    output += f"{key} IS NULL"
                elif isinstance(value, str):
                    output += f"{key}='{value}'"
                else:
                    output += f"{key}={value}"
            else:
                if value is None:
                    output += f"{key} IS NULL AND "
                elif isinstance(value, str):
                    output += f"{key}='{value}' AND "
                else:
                    output += f"{key}={value} AND "
        return output

    @staticmethod
    def __set_str(keys: tuple, values: tuple):
        output = ""
        for i, (key, value) in enumerate(zip(keys, values)):
            if i == len(keys) - 1:
                if isinstance(value, str):
                    output += f"{key}='{value}'"
                else:
                    output += f"{key}={value}"
            else:
                if isinstance(value, str):
                    output += f"{key}='{value}', "
                else:
                    output += f"{key}={value}, "
        return output

    @staticmethod
    def __orderby_str(keys: tuple, order: tuple) -> str:
        output = ""
        for i, (_key, _order) in enumerate(zip(keys, order)):
            if i == len(keys) - 1:
                output += f"{_key} {'DESC' if _order else ''}"
            else:
                output += f"{_key} {'DESC' if _order else ''}, "
        return output


class InterfaceError(Exception):
    pass


def main(args):
    from BowlingInterface import BowlingDate

    from dotenv import load_dotenv
    from os import getenv

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    try:
        # instance = GoogleSheetsInterface("1_FMEwtAsS_yEpspGJYuWvbnx-9QVAfdQimqE31W7pME", "TestSheet")
        instance = MariaDBInterface(getenv("MARIADB_USER"), getenv("MARIADB_PASS"), getenv("MARIADB_DB"))
    except APIConnectionError as err:
        print(err)
        return 1
    except mariadb.Error as err:
        print(err)
        return 1

    print(instance.add_row("data", ("date",), (BowlingDate.today(),)))


if __name__ == "__main__":
    from sys import argv

    main(argv)
