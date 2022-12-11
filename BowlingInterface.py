"""

BowlingInterface.py
Written by: William Lin

Description:
Interface to Bowling Score Tracker in Google Sheets. Utilizes GoogleSheetsInterface (created by William Lin)

"""

from GoogleSheetsInterface import GoogleSheetsInterface

class BowlingInterface:
    # Constructors
    def __init__(self, sheet_id: str, sheet_range: str):
        self.interface = GoogleSheetsInterface(sheet_id, sheet_range)
        if not self.interface.sheet:
            self.interface = None

    # Getters
    def get_game(self, date: str) -> int:
        data = self.interface.get_data(0, 1)
        if not data:
            return 0

        for r_num, row in enumerate(data, start=1):
            if row and row[0] == date:
                return r_num
        return 0

    def get_games_played(self, date: str) -> int:
        if not self.get_game(date):
            return 0

        data = self.interface.get_data(0, 2, self.get_game(date), 1)
        if not data:
            return 0

        r_num = 0
        for row in data:
            if int(row[1]) < r_num:
                break
            r_num += 1


        return r_num

    # Setters

    # Functions
    def new_game(self, date: str):


        return 0

    def modify_game(self, date: str):
        return 0

    def play_game(self, date: str = None, row: int = None):
        if not date: # if row is inputted
            return
        if not row: # if date is inputted
            return

    def print_game(self, date: str) -> bool:
        game_row = self.interface.get_val_index(date, 1, True)
        if not game_row:
            return False
        games_played = self.get_games_played(date)
        if not games_played:
            return False

        spacing = [
            8,  # Date
            4,  # Game
            3,  # Score
            1, 1,  # G1
            1, 1,  # G2
            1, 1,  # G3
            1, 1,  # G4
            1, 1,  # G5
            1, 1,  # G6
            1, 1,  # G7
            1, 1,  # G8
            1, 1,  # G9
            2, 1, 1,  # G10
            3, 3, 3, 3, 3,  # Scores pt.1
            3, 3, 3, 3, 3  # Scores pt.2
        ]

        justification = [
            False,  # Date
            True,  # Game
            True,  # Score
            False, False,  # G1
            False, False,  # G2
            False, False,  # G3
            False, False,  # G4
            False, False,  # G5
            False, False,  # G6
            False, False,  # G7
            False, False,  # G8
            False, False,  # G9
            True, False, False,  # G10
            True, True, True, True, True,  # Scores pt.1
            True, True, True, True, True  # Scores pt.2
        ]

        print("{} {} {}".format("Date".ljust(8), "Game", "Scr"), end=" ")
        print("{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - -".format(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), end=" ")
        print("{} {} {} {} {} {} {} {} {} {}".format("1".rjust(3), "2".rjust(3), "3".rjust(3), "4".rjust(3),
                                                     "5".rjust(3), "6".rjust(3), "7".rjust(3), "8".rjust(3),
                                                     "9".rjust(3), "10".rjust(3)), end="")
        print()

        self.interface.format_print(game_row+games_played-1, 34, game_row, 1, spacing, justification)
        return True

    def __game_loop(self, row: int):
        def parse_score(score: str, prev_score: str = None) -> int:
            if score == "x":
                return 10
            if score == "/":
                return 10 - parse_score(prev_score)
            if score == "-":
                return 0
            else:
                try:
                    return int(score)
                except ValueError:
                    return -1
        def user_input(frame_num: int, throw_num: int, pin_num: int):
            while 1:
                throw = input(f"Frame {frame_num}: Throw {throw_num}> ")

                if throw != "/" and 0 <= parse_score(throw) <= pin_num:
                    return throw
                else:
                    print("Invalid Input: " + throw)

        game_data = [
            "", "", # 1
            "", "", # 2
            "", "", # 3
            "", "", # 4
            "", "", # 5
            "", "", # 6
            "", "", # 7
            "", "", # 8
            "", "", # 9
            "", "", "" # 10
        ]

        frame = 1
        while frame < 10:
            num_pins = 10

            first_throw = user_input(frame, 1, num_pins)
            if parse_score(first_throw) == 10:
                game_data[2*(frame-1)] = "x"
                game_data[2*(frame-1)+1] = "-"
                frame += 1
                continue
            if 0 < parse_score(first_throw) < num_pins:
                game_data[2*(frame-1)] = first_throw
                num_pins -= parse_score(first_throw)
            elif parse_score(first_throw) == 0:
                game_data[2*(frame-1)] = "-"

            second_throw = user_input(frame, 2, num_pins)
            if parse_score(second_throw, first_throw) == num_pins:
                game_data[2*(frame-1)+1] = "/"
            elif 0 < parse_score(second_throw) < num_pins:
                game_data[2*(frame-1)+1] = second_throw
            elif parse_score(second_throw) == 0:
                game_data[2*(frame-1)+1] = "-"

            frame += 1

        num_pins = 10

        first_throw = user_input(10, 1, num_pins)
        if parse_score(first_throw) == 10:
            game_data[2*(10-1)] = "x"
        elif 0 < parse_score(first_throw) < num_pins:
            game_data[2*(10-1)] = first_throw
            num_pins -= parse_score(first_throw)
        elif parse_score(first_throw) == 0:
            game_data[2*(10-1)] = "-"

        second_throw = user_input(10, 2, num_pins)
        if first_throw == "x": # second throw strike condition
            if parse_score(second_throw) == 10:
                game_data[2*(10-1)+1] = "x"
            elif 0 < parse_score(second_throw) < num_pins:
                game_data[2*(10-1)+1] = second_throw
                num_pins -= parse_score(second_throw)
            elif parse_score(first_throw) == 0:
                game_data[2*(10-1)+1] = "-"
        else:
            if parse_score(second_throw, first_throw) == num_pins:
                game_data[2*(10-1)+1] = "/"
                num_pins = 10
            elif 0 < parse_score(second_throw) < num_pins:
                game_data[2*(10-1)+1] = second_throw
                return game_data
            elif parse_score(second_throw) == 0:
                game_data[2*(10-1)+1] = "-"
                return game_data

        third_throw = user_input(10, 3, num_pins)
        if second_throw == "x" or second_throw == "/": # third throw strike condition
            if parse_score(third_throw) == 10:
                game_data[2*(10-1)+2] = "x"
            elif 0 < parse_score(third_throw) < num_pins:
                game_data[2*(10-1)+2] = third_throw
                return game_data
            elif parse_score(third_throw) == 0:
                game_data[2*(10-1)+2] = "-"
                return game_data
        else:
            if parse_score(third_throw, second_throw) == num_pins:
                game_data[2*(10-1)+2]  = "/"
                return game_data
            elif 0 < parse_score(third_throw, second_throw) < num_pins:
                game_data[2*(10-1)+2] = third_throw
                return game_data
            elif parse_score(third_throw) == 0:
                return game_data

        return game_data

    def game_loop_test(self):
        return self.__game_loop(0)


SPREADSHEET_ID = None
SPREADSHEET_RANGE = None

def main(args):
    global SPREADSHEET_ID, SPREADSHEET_RANGE

    from dotenv import load_dotenv
    from os import getenv

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    SPREADSHEET_ID = getenv('SPREADSHEET_ID')
    SPREADSHEET_RANGE = getenv('SPREADSHEET_TEST_RANGE')

    instance = BowlingInterface(SPREADSHEET_ID, SPREADSHEET_RANGE)

    print(instance.game_loop_test())

if __name__ == "__main__":
    from sys import argv

    main(argv)
