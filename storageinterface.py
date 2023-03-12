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
from os.path import exists as token_exists

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import mariadb


class GoogleSheetInterface:
    def __init__(self, spreadsheet_id: str, sheet_name: str):
        self.valid = True
        self.err = None

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

    def add_row(self, col: int, row: int, data: list):
        request = self.sheet

        try:
            request.execute()
        except Exception as err:
            print("Exception happened in `add_row`")
            print(f"Trace: {err}")

    def get_row(self):
        return

    def set_row(self):
        return

    def del_row(self):
        return

    def purge_table(self):
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

    @staticmethod
    def get_abc_col(col: int) -> str:
        def get_letter(num: int) -> str:
            return chr(65 + num)

        output = ""
        a = col
        while a > 0:
            b = (a - 1) % 26
            a = (a - 1) // 26
            output = get_letter(b) + output
        return output


class MariaDBInterface:
    def __init__(self, user: str, password: str, database: str):
        self.valid = True
        self.err = None

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
    def purge_table(self, table: str, confirm: bool):
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


class InternetError(Exception):
    pass


def main(args):
    from BowlingTools import DateUtils

    from dotenv import load_dotenv
    from os import getenv

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    try:
        instance = GoogleSheetInterface("1_FMEwtAsS_yEpspGJYuWvbnx-9QVAfdQimqE31W7pME", "TestSheet")
        # instance = MariaDBInterface(getenv("MARIADB_USER"), getenv("MARIADB_PASS"), getenv("MARIADB_DB"))
    except mariadb.Error as err:
        print(err)
        return 1

    print(instance.add_row())


if __name__ == "__main__":
    from sys import argv

    main(argv)
