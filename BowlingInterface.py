import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2.error import ServerNotFoundError

class BowlingInterface:
    # Constructors
    def __init__(self, sheet_id: str, sheet_range: str):
        print("Checking for API tokens...")
        creds = None
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        if os.path.exists("token.json"):
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
        print("Checking of API tokens successful")
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
            print("Getting spreadsheet resources successful\n")

            print("Testing Http calls...")
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range
            ).execute()

        except HttpError as err:
            print("Http call testing failed")
            print("Check if Sheet ID and/or Sheet Range is valid")
            print("Traceback:")
            print(err)
            self.sheet = None
            return

        except ServerNotFoundError as err:
            print("Http call testing failed")
            print("Check internet connection")
            print("Traceback:")
            print(err)
            self.sheet = None
            return

        print("Http call testing successful\n")

    # Getters and Setters
    def get_data(self, data: str = "all"):
        if data == "date":
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range + '!A:A'
            ).execute()
        elif data == "dategame":
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range + '!A:B'
            ).execute()
        elif data == "totalscore":
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range + '!C:C'
            ).execute()
        else:
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_range
            ).execute()

        values = result.get(
            "values",
            []
        )

        if not values:
            print("No data found.")
            return None
        else:
            return values

    def get_empty_row(self) -> int:
        data = self.get_data("dategame")
        r = 0
        for r, row in enumerate(data, start=1):
            continue
        return r + 1

    def get_games_played(self, date: str) -> int:
        data = self.get_data("dategame")
        date_exists = False

        n_games = None
        for r, row in enumerate(data, start=1):
            if not date_exists:
                if not row:
                    continue
                elif row[0] == date:
                    n_games = 1
                    date_exists = True
            else:
                if n_games < int(row[1]):
                    n_games = int(row[1])
                else:
                    return n_games
        return n_games if date_exists else -1

    def get_date(self, date: str) -> int:
        data = self.get_data("date")
        for r, row in enumerate(data, start=1):
            if not row:
                continue
            elif row[0] == date:
                return r
        return -1

    # Functions
    def new_game(self, date: str) -> int:  # TODO: creates and returns row of new day created
        def get_frames(row: str, frame: int) -> (str, str, str, str, str):
            if frame == 1:
                return f"F{row}", "", f"E{row},F{row}", f"G{row},H{row}", f"I{row},J{row}"
            elif frame == 2:
                return f"H{row}", f"AA{row}+", f"G{row},H{row}", f"I{row},J{row}", f"K{row},L{row}"
            elif frame == 3:
                return f"J{row}", f"AB{row}+", f"I{row},J{row}", f"K{row},L{row}", f"M{row},N{row}"
            elif frame == 4:
                return f"L{row}", f"AC{row}+", f"K{row},L{row}", f"M{row},N{row}", f"O{row},P{row}"
            elif frame == 5:
                return f"N{row}", f"AD{row}+", f"M{row},N{row}", f"O{row},P{row}", f"Q{row},R{row}"
            elif frame == 6:
                return f"P{row}", f"AE{row}+", f"O{row},P{row}", f"Q{row},R{row}", f"S{row},T{row}"
            elif frame == 7:
                return f"R{row}", f"AF{row}+", f"Q{row},R{row}", f"S{row},T{row}", f"U{row},V{row}"
            elif frame == 8:
                return f"T{row}", f"AG{row}+", f"S{row}:T{row}", f"U{row},V{row}", f"W{row},0"
            elif frame == 9:
                return f"V{row}", f"AH{row}+", f"U{row}:V{row}", f"W{row},X{row}", f"0,0"
            elif frame == 10:
                return f"Y{row}", f"AI{row}+", f"W{row}:X{row}", f"Y{row}", "0"

        def score_func(row: str, frame: int) -> str:
            blank, prev_score, curr_fr, next_fr, next_next_fr = get_frames(row, frame)
            output = "=IF("
            output += "ISBLANK(" + blank + "),"
            output += '"",'
            output += prev_score
            output += "B_SCORE_FRAME("
            output += "B_CALC_FRAME(" + curr_fr + "),"
            if frame == 10:
                output += "B_PARSE(" + next_fr + "),"
                output += "0"
            else:
                output += "B_CALC_BONUS(" + curr_fr + "," + next_fr + "),"
                output += "B_CALC_DOUBLE(" + curr_fr + "," + next_fr + "," + next_next_fr + ")"
            output += ")"
            output += ")"
            return output

        r_game_int = self.get_empty_row()
        r_game_str = str(r_game_int)
        today_dategame_rc = "!A" + r_game_str + ":B" + r_game_str
        today_total_score_rc = "!AA" + r_game_str + ":AJ" + r_game_str
        dategame_setup = self.sheet_range + today_dategame_rc
        score_setup = self.sheet_range + today_total_score_rc

        values = [
            [date,
             "=IF(ISDATE(INDIRECT(ADDRESS(ROW(),COLUMN()-1,4))),1,INDIRECT(ADDRESS(ROW()-1,COLUMN(),4))+1)"
             ]
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().append(
            spreadsheetId=self.sheet_id,
            range=dategame_setup,
            valueInputOption="USER_ENTERED",
            body=body
        )
        request.execute()

        values = [
            [score_func(r_game_str, 1),
             score_func(r_game_str, 2),
             score_func(r_game_str, 3),
             score_func(r_game_str, 4),
             score_func(r_game_str, 5),
             score_func(r_game_str, 6),
             score_func(r_game_str, 7),
             score_func(r_game_str, 8),
             score_func(r_game_str, 9),
             score_func(r_game_str, 10)]
        ]
        body = {
            "values": values
        }

        request = self.sheet.values().update(
            spreadsheetId=self.sheet_id,
            range=score_setup,
            valueInputOption="USER_ENTERED",
            body=body
        )
        request.execute()

        return r_game_int

    def modify(self):
        return

    def print_game(self, date: str) -> int:
        try:
            data = self.get_data()
        except HttpError as err:
            print(err)
            return 1

        r_date = self.get_date(date)
        n_games = self.get_games_played(date)

        if r_date == -1 or n_games == -1:
            return 1

        print("{0:8} {1:4} {2:5}"
              .format("Date", "Game", "Score"), end=" ")
        print("|", end=" ")
        print("{0:5} {1:5} {2:5} {3:5} {4:5} {5:5} {6:5} {7:5} {8:5} {9:8}"
              .format("FRME1", "FRME2", "FRME3", "FRME4", "FRME5", "FRME6", "FRME7", "FRME8", "FRME9", "FRME10"),
              end=" ")
        print("|", end=" ")
        print("{0:3} {1:3} {2:3} {3:3} {4:3} {5:3} {6:3} {7:3} {8:3} {9:3}"
              .format("GM1", "GM2", "GM3", "GM4", "GM5", "GM6", "GM7", "GM8", "GM9", "GM10"))
        for r, row in enumerate(data, start=1):
            if r == 1 or r < r_date:
                continue
            if r >= r_date + n_games:
                break
            for c, col in enumerate(row, start=1):
                if c == 1:  # Date
                    print("{0:8}".format(col), end=" ")
                elif c == 2:  # Game
                    print("{0:^4}".format(col), end=" ")
                elif c == 3:  # Score
                    print("{0:^5}".format(col), end=" ")
                elif c == 4:  # Spacer
                    print("|", end=" ")
                elif 5 <= c <= 25:  # Frame 1 - 10
                    print("{0:2}".format(col), end=" ")
                elif c == 26:  # Spacer 2
                    print("|", end=" ")
                elif 27 <= c <= 35:  # Game 1 - 9 Score
                    print("{0:>3}".format(col), end=" ")
                elif c == 36:  # Game 10 Score
                    print("{0:>4}".format(col), end="")
            print()
        return 0
