"""

BowlingInterface.py
Written by: William Lin

Description:
Interface to Bowling Score Tracker in Google Sheets. Utilizes StorageInterfaces.py (created by William Lin)

"""

from StorageInterface import MariaDBInterface
from StorageInterface import GoogleSheetInterface
from StorageInterface import InterfaceError

from datetime import datetime as t_datetime
from datetime import date as t_date
from dateutil.parser import parse as parse_date
from dateutil.parser import parserinfo


class Interface:
    def __init__(self, username: str, password: str, database: str,
                 sheet_id: str, sheet_range: str,
                 debug: bool = False):
        self.valid = True
        self.offline = False
        self.err: list = []
        self.debug = debug

        self.interface = MariaDBInterface(username, password, database)
        # self.backup = GoogleSheetInterface(sheet_id, sheet_range)

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

    def delete_game(self, date: str, game: int) -> bool:
        if not self.get_game(date, game):
            return False

        self.interface.del_row("data", ("date", "game",), (date, game,))
        return True

    def add_frame(self, date: str, game: int, frame: int, frame_score: list[int]):
        self.interface.set_row("data", (f"f{frame}_1",), (frame_score[0],), ("date", "game",), (date, game,))
        if len(frame_score) == 2:
            self.interface.set_row("data", (f"f{frame}_2",), (frame_score[1],), ("date", "game",), (date, game,))
        if frame == 10 and len(frame_score) == 3:
            self.interface.set_row("data", (f"f{frame}_3",), (frame_score[2],), ("date", "game",), (date, game,))

    def modify_frame(self, date: str, game: int, frame: int, throw: int, value: int):
        self.interface.set_row("data", (f"f{frame}_{throw}",), (value,), ("date", "game",), (date, game,))

    def add_score(self, date: str, game: int, frame: int, value: int):
        self.interface.set_row("data", (f"f{frame}_s",), (value,), ("date", "game",), (date, game,))

    def pull_data(self, date: str, game: int):
        # TODO: Pull data from backup

        return

    def push_data(self, date: str, game: int):
        # TODO: Push data to backup

        return

    def check_diff(self) -> list[tuple[t_date, int]]:
        # TODO: Checks if there are any differences between local database and backup
        # For efficiency, first check dates and number of games,

        pass


class GameUtils:
    @staticmethod
    def score_to_num(score: str, pins_left: int) -> int | None:
        if (pins_left == 10 and score == "/") or (pins_left != 10 and score == "x"):
            return None
        if score == "x":
            return 10
        elif pins_left and score == "/":
            return pins_left
        elif score == "-":
            return 0
        else:
            try:
                val = int(score)
            except ValueError:
                return None
            if 0 <= val <= pins_left:
                return val
            else:
                return None

    @staticmethod
    def is_int(value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError or TypeError:
            return False

    @staticmethod
    def to_int(value: str) -> int | None:
        try:
            return int(value)
        except ValueError or TypeError:
            return None

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
        if 1 <= frame <= 9 and not GameUtils.score_to_num(str(data[1]), 10 - data[0]):
            return False
        if frame == 10 and data[0] != 10 and (data[0] + data[1]) != 10 and data[2] != 0:
            return False
        return True

    @staticmethod
    def calc_frame_scores(data: list[int]) -> list[int]:
        def parse_score(a, b, c, d, e):
            if a == 10 and c == 10 and e == 10:  # Turkey
                return a + c + e
            elif a == 10 and c == 10:  # Double
                return a + c + e
            elif a == 10:  # Strike
                return a + c + d
            elif a + b == 10:  # Spare
                return a + b + c
            else:  # Everything Else
                return a + b

        cumulated_score = [0] * 10

        for i, tf1, tf2, nf1, nf2, nnf1 in zip(range(0, 8),
                                               data[0:19:2], data[1:19:2], data[2:19:2], data[3:19:2], data[4:19:2]):
            cumulated_score[i] = parse_score(tf1, tf2, nf1, nf2, nnf1)

        cumulated_score[8] = parse_score(data[16], data[17], data[18], data[19], data[19])

        if data[20]:
            cumulated_score[9] = data[18] + data[19] + data[20]
        else:
            cumulated_score[9] = data[18] + data[19]

        return cumulated_score

    @staticmethod
    def accumulate_scores(cumulated_scores: list[int]) -> list[int]:
        accumulated_scores = [0] * 10
        running_sum = 0

        for i, number in enumerate(cumulated_scores):
            running_sum += number
            accumulated_scores[i] = running_sum

        return accumulated_scores

    @staticmethod
    def verify_game(game_data: list[int | None]) -> bool:
        # TODO: verify that input list is a valid game

        ident, frame_scores, scores = game_data[:3], game_data[3:24], game_data[24:]
        print(ident)
        print(frame_scores)
        print(scores)

        return True


class DateUtils:
    @staticmethod
    def is_date(value: str, dateformat: str = None) -> bool:
        try:
            if dateformat:
                t_datetime.strptime(value, dateformat)
            else:
                parse_date(value, parserinfo(False, False))
            return True
        except ValueError or TypeError:
            return False

    @staticmethod
    def to_date(value: str, dateformat: str = None) -> t_date | None:
        try:
            if dateformat:
                return t_datetime.strptime(value, dateformat).date()
            else:
                return parse_date(value, parserinfo(False, False)).date()
        except ValueError or TypeError as err:
            return None

    @staticmethod
    def today(dateformat: str = "%Y-%m-%d") -> str:
        return t_date.today().strftime(dateformat)

    @staticmethod
    def format_date(date: t_date, dateformat: str = "%Y-%m-%d") -> str | None:
        if not date:
            return None

        return date.strftime(dateformat)


def main(args):
    from dotenv import load_dotenv
    from os import getenv

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    instance = Interface(
        getenv('MARIADB_USER'),
        getenv('MARIADB_PASS'),
        getenv('MARIADB_DB'),
        getenv('SPREADSHEET_ID'),
        getenv('SPREADSHEET_TEST_RANGE')
    )

    instance.add_score("2022-01-01", 1, 1, 1, 5)


if __name__ == "__main__":
    from sys import argv

    main(argv)
