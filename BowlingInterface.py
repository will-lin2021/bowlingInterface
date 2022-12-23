"""

BowlingInterface.py
Written by: William Lin

Description:
Interface to Bowling Score Tracker in Google Sheets. Utilizes GoogleSheetsInterface (created by William Lin)

"""

from GoogleSheetsInterface import GoogleSheetsInterface
from GoogleSheetsInterface import APIConnectionError

from datetime import datetime as dt


class BowlingInterface:
    # Constructors
    def __init__(self, sheet_id: str, sheet_range: str):
        try:
            self.valid = True
            self.interface = GoogleSheetsInterface(sheet_id, sheet_range)

            if not self.interface.sheet:
                self.valid = False
                return
        except APIConnectionError as err:
            self.valid = False
            return

    # Getters
    def get_game_row(self, date: str) -> int:
        return self.interface.get_value_index(date, 1, True)

    def get_games_played(self, date: str) -> int:
        game_row = self.get_game_row(date)
        if not game_row:
            return 0

        data = self.interface.get_data(0, 2, game_row, 1)
        if not data:
            return 0

        num_games = 0
        for row in data:
            if num_games and row[0] and row[1]:
                break
            num_games += 1

        return num_games

    # Setters

    # Functions
    def play_game(self, date: str):
        def print_help_menu(option: str = None):
            if option == 't':
                print("Menu for entering frame results")
                print("\tusage: 't'")
            elif option == 'm':
                print("Modify existing frame")
                print("\tusage: 'm <frame> <args>'")
            elif option == 'q':
                print("Exits game")
                print("\tusage: 'q <opt option>'")
                print("\toptions:")
                print("\t\t'l': exit without clearing data")
            else:
                print(" Game Commands ".center(60, "="))
                print("{:1} | {}".format("e", "enter results"))
                print("{:1} | {}".format("m", "modify frame"))
                print("{:1} | {}".format("q", "exit"))
                print("{:1} | {}".format("?", "print this menu"))
                print("Call '? <cmd>' for help with specific commands")

        def print_curr_game(game_scores: list):
            print("| {} - | {} - | {} - | {} - | {} - | {} - | {} - | {} - | {} - | {} - - |"
                  .format(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))

            print("|", end=" ")
            for frame_no in range(1, 11):
                if frame_no == 10:
                    print("", end=" ")
                print(game_scores[2 * (frame_no - 1)].center(1), end=" ")

                if frame_no == 10 or game_scores[2 * (frame_no - 1)] != "x":
                    print(game_scores[2 * (frame_no - 1) + 1].center(1), end=" ")
                else:
                    print(" ", end=" ")
                if frame_no == 10:
                    print(game_scores[2 * (frame_no - 1) + 2].center(1), end=" ")
                print("|", end=" ")
            print()

        def as_num(this_input: str, pins_left: int = 0):
            if pins_left != 10 and this_input == "x":
                return -1

            if this_input == "x":
                return 10
            elif pins_left and this_input == "/":
                return pins_left
            elif this_input == "-":
                return 0
            else:
                try:
                    val = int(this_input)
                    if 0 <= val <= pins_left:
                        return val
                    else:
                        return -1
                except ValueError:
                    return -1

        frame = 1
        throw = 1
        num_pins = 10
        throw1_clear = False
        throw2_clear = False
        game_data = ["" for _ in range(21)]

        done = False
        while not done:
            user_input = input("Game> ").strip()
            user_inputs = user_input.split()
            command = user_inputs[0] if user_inputs else ""
            args = user_inputs[1:]

            if command == 'q':
                return
            elif command == '?':
                if len(args) == 1:
                    print_help_menu(args[0])
                else:
                    print_help_menu()
            elif command == 't':
                while frame <= 10:
                    print_curr_game(game_data)
                    print(frame, throw, throw1_clear, throw2_clear)
                    frame_input = input(f"Frame {frame} Throw {throw} (c to exit)> ")
                    frame_input_val = as_num(frame_input, num_pins)
                    if frame_input == 'c':
                        break
                    if frame_input_val == -1:
                        print("Invalid Input: '" + frame_input + "'")

                    if throw == 1:  # throw 1
                        print("this is the first throw")
                        if frame_input_val == num_pins:
                            print("strike")
                            game_data[2 * (frame - 1)] = "x"

                            if frame < 10:  # frames 1-9
                                game_data[2 * (frame - 1) + 1] = "-"
                                frame += 1
                            else:  # frame 10
                                throw += 1
                                throw1_clear = True
                        elif 0 < frame_input_val < num_pins:
                            print("hit something")
                            game_data[2 * (frame - 1)] = frame_input

                            num_pins -= frame_input_val
                            throw += 1
                        elif frame_input_val == 0:
                            print("miss")
                            game_data[2 * (frame - 1)] = "-"

                            throw += 1
                    elif throw == 2:  # throw 2
                        print("This is second throw")
                        if not throw1_clear and frame_input_val == num_pins:
                            print("spare")
                            game_data[2 * (frame - 1) + 1] = "/"

                            if frame < 10:  # frame 1-9
                                frame += 1
                                throw -= 1
                                num_pins = 10
                            else:  # frame 10
                                throw += 1
                                num_pins = 10
                                throw2_clear = True
                        elif frame_input_val == num_pins:  # only reachable at frame 10
                            print("strike")
                            game_data[2 * (frame - 1) + 1] = "x"

                            throw += 1
                            throw2_clear = True
                        elif not throw1_clear and 0 < frame_input_val < num_pins:
                            print("hit some more stuff")
                            game_data[2 * (frame - 1) + 1] = frame_input

                            if frame < 10:  # frame 1-9
                                frame += 1
                                throw -= 1
                                num_pins = 10
                            else:  # frame 10
                                frame += 1
                                throw += 1
                                num_pins -= frame_input_val
                                done = True
                        elif 0 < frame_input_val < num_pins:  # only reachable at frame 10
                            print("second shot")
                            game_data[2 * (frame - 1) + 1] = frame_input

                            throw += 1
                            num_pins -= frame_input_val
                        elif not throw1_clear and frame_input_val == 0:
                            print("miss")
                            game_data[2 * (frame - 1) + 1] = "-"


                            if frame < 10:  # frame 1-9
                                frame += 1
                                throw -= 1
                                num_pins = 10
                            else:  # frame 10
                                frame += 1
                                throw += 1
                                done = True
                        elif frame_input_val == 0:  # only reachable at frame 10
                            print("miss")
                            game_data[2 * (frame - 1) + 1] = "-"
                            game_data[2 * (frame - 1) + 2] = "-"

                            throw += 1
                    elif (throw1_clear or throw2_clear) and throw == 3:  # only frame 10
                        print("This is third shot")
                        if not throw2_clear and frame_input_val == num_pins:
                            print("spare")
                            game_data[2 * (frame - 1) + 2] = "/"

                            frame += 1
                        elif throw2_clear and frame_input_val == num_pins:
                            print("strike")
                            game_data[2 * (frame - 1) + 2] = "x"

                            frame += 1
                        elif 0 < frame_input_val < num_pins:
                            print("last shot")
                            game_data[2 * (frame - 1) + 2] = frame_input

                            frame += 1
                        elif frame_input_val == 0:
                            print("miss")
                            game_data[2 * (frame - 1) + 2] = "-"

                            frame += 1
                        done = True
                    print()

            elif command == 'm':
                if len(args) > 1:
                    print()
                print("modify menu")
            else:
                print("Invalid Input: '" + user_input + "'")
            print()

        print("Final Scores")
        print_curr_game(game_data)
        row, games_played = self.__game_init(date)
        self.__game_setup(row)
        self.__game_data_push(row, game_data)

    def modify_game(self, date: str):
        return

    def __game_init(self, date: str):
        data = self.interface.get_data(0, 1, 2, 1)
        prev_date = None
        curr_date = dt.strptime(date, "%m/%d/%y")
        existing_date = False

        for _date in data:
            if not _date:
                continue
            search_date = dt.strptime(_date[0], "%m/%d/%y")

            if curr_date == search_date:
                prev_date = search_date
                existing_date = True
                break
            if curr_date < search_date:
                break

            prev_date = search_date

        prev_date = prev_date.strftime("%m/%d/%y") if prev_date else None
        curr_date = curr_date.strftime("%m/%d/%y")

        row = self.get_game_row(prev_date) if prev_date else 2
        games_played = self.get_games_played(prev_date) if prev_date else 0

        row += games_played

        self.interface.add_row(row)

        if not existing_date:
            self.interface.set_cell(row, 1, curr_date)
            games_played = 0

        return row, games_played

    def __game_setup(self, row: int):
        def score_setup(prev_val, col1, col2, col3, col4, col5):
            return f"=IF(ISBLANK({col2}{row}),\"\",{f'{prev_val}{row}+' if prev_val else ''}" \
                   f"B_SCORE_FRAME(B_CALC_FRAME({col1}{row},{col2}{row})," \
                   f"B_CALC_BONUS({col1}{row},{col2}{row},{col3}{row},{f'{col4}{row}' if col4 else ''}," \
                   f"{f'{col5}{row}' if col5 else ''})))"

        game_num_setup = "=IF(ISDATE(INDIRECT(ADDRESS(ROW(),COLUMN()-1,4))),1,INDIRECT(ADDRESS(ROW()-1,COLUMN(),4))+1)"
        success = self.interface.set_cell(row, 2, game_num_setup)
        if not success:
            return success

        score_setup = [
            score_setup("", "D", "E", "F", "G", "H"),
            score_setup("Y", "F", "G", "H", "I", "J"),
            score_setup("Z", "H", "I", "J", "K", "L"),
            score_setup("AA", "J", "K", "L", "M", "N"),
            score_setup("AB", "L", "M", "N", "O", "P"),
            score_setup("AC", "N", "O", "P", "Q", "R"),
            score_setup("AD", "P", "Q", "R", "S", "T"),
            score_setup("AE", "R", "S", "T", "U", "V"),
            score_setup("AF", "T", "U", "V", "W", "W"),
            score_setup("AG", "V", "W", "X", "", "")
        ]
        success = self.interface.set_row(row, 25, score_setup)
        if not success:
            return success

        stats_setup = [
            f"=COUNTIF(D{row}:X{row}, \"x\")/12",
            f"=COUNTIF(D{row}:X{row}, \"/\")/12",
            f"=AI{row}+AJ{row}"
        ]
        success = self.interface.set_row(row, 35, stats_setup)
        if not success:
            return success

    def __game_data_push(self, row, frame_data: list):
        self.interface.set_row(row, 4, frame_data)

    def print_game(self, date: str) -> bool:
        game_row = self.interface.get_value_index(date, 1, True)
        if not game_row:
            return False
        games_played = self.get_games_played(date)
        if not games_played:
            return False

        spacing = [
            8, 4, 3,  # Date, Game, Score
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
            3, 3, 3, 3, 3,  # Scores pt.2
            7, 7, 7  # Strike%, Spare%, Total%
        ]

        justification = [
            False, True, True,  # Date, Game, Score
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
            True, True, True, True, True,  # Scores pt.2
            False, False, False  # Strike%, Spare%, Total%
        ]

        print("{} {} {}".format("Date".ljust(8), "Game", "Scr"), end=" ")
        print("{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - -".format(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), end=" ")
        print("{} {} {} {} {} {} {} {} {} {}".format("1".rjust(3), "2".rjust(3), "3".rjust(3), "4".rjust(3),
                                                     "5".rjust(3), "6".rjust(3), "7".rjust(3), "8".rjust(3),
                                                     "9".rjust(3), "10".rjust(3)), end=" ")
        print("{} {} {}".format("Strike%".ljust(7), "Spare%".ljust(7), "Total%".ljust(7)))

        self.interface.format_print(game_row + games_played - 1, 37, game_row, 1, spacing, justification)
        return True


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


if __name__ == "__main__":
    from sys import argv

    main(argv)
