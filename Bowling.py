"""

BowlingInterface.py
Written by: William Lin

Description:
Interface to Bowling Score Tracker in Google Sheets. Utilizes StorageInterfaces.py (created by William Lin)

"""

from StorageInterfaces import MariaDBInterface
from StorageInterfaces import GoogleSheetInterface
from StorageInterfaces import InterfaceError

from datetime import datetime as t_datetime
from datetime import date as t_date
from dateutil import parser


class BowlingInterface:
    def __init__(self, username: str, password: str, database: str, sheet_id: str, sheet_range: str):
        self.valid = True
        self.interface = MariaDBInterface(username, password, database)
        # self.backup = GoogleSheetInterface(sheet_id, sheet_range)
        self.err: tuple = ()

        if not self.interface.valid:
            self.valid = False
            self.err += self.interface.err
        # if not self.backup.valid:
        #     self.valid = False
        #     self.err += self.interface.err

    def get_games_played(self, date: str) -> int:
        return len(self.interface.get_row("data", ("date",), (date,)))

    def get_game(self, date: str, game: int = None) -> list:
        if not game:
            return self.interface.get_row("data", ("date",), (date,))
        else:
            return self.interface.get_row("data", ("date", "game"), (date, game))

    def new_game(self, date: str):
        games_played = self.get_games_played(date)
        if not games_played:
            self.interface.add_row("data", ("date", "game",), (date, 1,))
        else:
            self.interface.add_row("data", ("date", "game",), (date, games_played + 1,))

    def delete_game(self, date: str, game: int):
        self.interface.del_row("data", ("date", "game",), (date, game,))

    def add_score(self, date: str, game: int, frame: int, throw: int, value: int):
        self.interface.set_row("data", (f"f{frame}_{throw}",), (value,), ("date", "game",), (date, game,))

    def modify_score(self, date: str, game: int, frame: int, throw: int, value: int):
        self.interface.set_row("data", (f"f{frame}_{throw}",), (value,), ("date", "game",), (date, game,))

    def pull_data(self):
        return

    def push_data(self):
        return

    def check_diff(self):
        return

    def close(self):
        self.interface.conn.close()
        self.interface = None
        # self.backup = None


class BowlingUtils:
    @staticmethod
    def verify_frame(frame: int, data: list[int]) -> bool:
        if not frame:
            return False
        if 1 <= frame <= 9 and len(data) != 2:
            return False
        if frame == 10 and len(data) != 3:
            return False
        if None in data:
            return False
        if 1 <= frame <= 9 and not BowlingParser.parse_as_num(str(data[1]), 10 - data[0]):
            return False
        if frame == 10 and data[0] != 10 and (data[0] + data[1]) != 10 and data[2] != 0:
            return False
        return True

    @staticmethod
    def calculate_scores(data: list) -> list:
        def parse_score(a, b, c, d, e):
            if a == 10 and c == 10 and e == 10:
                return a + c + e
            elif a == 10 and c == 10:
                return a + c + e
            elif a == 10:
                return a + c + d
            elif a + b == 10:
                return a + b + c
            else:
                return a + b

        for i, _data in enumerate(data):
            print(i, _data)

        cumulated_score = [None for i in range(10)]

        for i, a, b, c, d, e in zip(range(0, 7), range(0, 19, 2), range(1, 20, 2),
                                    range(2, 21, 2), range(3, 22, 2), range(4, 23, 2)):
            cumulated_score[i] = parse_score(data[a], data[b], data[c], data[d], data[e])

        cumulated_score[7] = parse_score(data[14], data[15], data[16], data[17], data[18])
        cumulated_score[8] = parse_score(data[16], data[17], data[18], data[19], data[19])

        if data[20]:
            cumulated_score[9] = data[18] + data[19] + data[20]
        else:
            cumulated_score[9] = data[18] + data[19]

        return cumulated_score

    @staticmethod
    def accumulate_scores(cumulated_scores: list):
        accumulated_scores = [None for i in range(10)]
        running_sum = 0

        for i, number in enumerate(cumulated_scores):
            running_sum += number
            accumulated_scores[i] = running_sum

        return accumulated_scores


class BowlingDate:
    @staticmethod
    def today(dateformat: str = "%Y-%m-%d") -> str:
        return t_date.today().strftime(dateformat)

    @staticmethod
    def format_date(date: t_date, dateformat: str = "%Y-%m-%d") -> str | None:
        if not date:
            return None

        return date.strftime(dateformat)


class BowlingParser:
    @staticmethod
    def parse_as_num(curr: str, pins_left: int = None) -> int | None:
        if (pins_left == 10 and curr == "/") or (pins_left != 10 and curr == "x"):
            print(pins_left)
            return None
        if curr == "x":
            return 10
        elif pins_left and curr == "/":
            return pins_left
        elif curr == "-":
            return 0
        else:
            try:
                val = int(curr)
            except ValueError:
                return None
            if 0 <= val <= pins_left:
                return val
            else:
                return None

    @staticmethod
    def is_num(inp) -> bool:
        try:
            int(inp)
            return True
        except ValueError or TypeError:
            return False

    @staticmethod
    def as_num(inp) -> int | None:
        try:
            return int(inp)
        except ValueError or TypeError:
            return None

    @staticmethod
    def is_date(inp) -> bool:
        try:
            t_datetime.strptime(inp, "%m/%d/%y")
            return True
        except ValueError or TypeError:
            return False

    @staticmethod
    def as_date(inp) -> t_date | None:
        try:
            return t_datetime.strptime(inp, "%m/%d/%y").date()
        except ValueError or TypeError:
            return None


def main(args):
    from dotenv import load_dotenv
    from os import getenv

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    instance = BowlingInterface(
        getenv('MARIADB_USER'),
        getenv('MARIADB_PASS'),
        getenv('MARIADB_DB'),
        getenv('SPREADSHEET_ID'),
        getenv('SPREADSHEET_TEST_RANGE')
    )

    instance.add_score("2022-01-01", 1, 1, 1, 5)

    BowlingUtils.Test


if __name__ == "__main__":
    from sys import argv

    main(argv)
