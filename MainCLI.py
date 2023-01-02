"""

mainCLI.py
Written by: William Lin

Description:
Command Line Interface (CLI) for Bowling Score Tracker

"""
import Bowling
from Bowling import BowlingInterface
from Bowling import BowlingUtils
from Bowling import BowlingDate
from Bowling import BowlingParser

from dotenv import load_dotenv
from os import getenv


def print_help_menu(option: str = None):
    if option == 'n':
        print("===== Create New Game ".ljust(30, "="))
        print("Creates a new game. If no date is provided, defaults to today")
        print("\tDate in `month/day/year` format (ex `1/1/99` or `01/01/99` or `01/01/1999`")
        print("\t\tusage: 'n <opt date>'")
    elif option == 'm':
        print("Modifies an existing game. ")
        print("If `throw` is inputted, specific throw will be modified. If not, entire frame will be modified")
        print("Date in `month/day/year` format (ex `1/1/99` or `01/01/99` or `01/01/1999`")
        print("\tusage:'m <date> <game>'")
    elif option == 'p':
        print("Prints game or games on given date")
        print("Date in `month/day/year` format (ex `1/1/99` or `01/01/99` or `01/01/1999`")
        print("\tusage: 'p <date> <opt: game>'")
    elif option == 'd':
        print("Deletes game on give date")
        print("\tusage: 'd <date> <game> <opt_args...>'")
        print("\topt_args:")
        print("\t\tforce: bypass confirmation message")
        print("\t\tnofill: delete without moving games to fill game number")
        print("\t\tall: deletes all games on given date, ignores game input")
    elif option == 'q':
        print("Quit Bowling Interface")
        print("\tusage: 'q'")
    else:
        print(" Interface Commands ".center(60, "="))
        print("{:1} | {}".format("n", "new game"))
        print("{:1} | {}".format("m", "modify game"))
        print("{:1} | {}".format("p", "print game"))
        print("{:1} | {}".format("d", "delete game"))
        print("{:1} | {}".format("q", "quit"))
        print("{:1} | {}".format("?", "print this menu"))
        print("Call '? <cmd>' for help with specific commands")


def game_start(instance: BowlingInterface, date: str):
    # TODO: Deal with case when there game number is not continuous

    game_number = instance.get_games_played(date) + 1
    print(f" Date: {date}, Game Number: {game_number} ".center(60, "="))
    instance.new_game(date)

    result = game_loop(instance, date, game_number)
    if result:
        frame_data = instance.get_game(date, game_number)[0][3:24]

        BowlingUtils.calculate_scores(frame_data)

        print("Game Complete")
    else:
        print("Game Incomplete")


def game_loop(instance: BowlingInterface, date: str, game: int) -> bool:
    frame = 1
    throw = 1
    num_pins = 10
    throw1_clear = False
    throw2_clear = False

    while frame <= 10:
        while 1:
            user_input = input(f"Frame {frame} Throw {throw} (m to modify previous score, q to quit)> ")
            user_input_val = BowlingParser.parse_as_num(user_input, num_pins)
            if user_input == 'm':
                modify_loop(instance, date, game)
                continue
            elif user_input == 'q':
                instance.delete_game(date, game)
                return False
            if user_input_val is None:
                print("Invalid Input: '" + user_input + "'")
                continue
            break

        instance.add_score(date, game, frame, throw, user_input_val)

        if 1 <= frame <= 9:
            if throw == 1:
                if user_input_val == 10:
                    frame += 1
                    num_pins = 10
                else:
                    throw += 1
                    num_pins -= user_input_val
            else:
                frame += 1
                throw -= 1
                num_pins = 10
        elif frame == 10:
            if throw == 1:
                if user_input_val == 10:
                    num_pins = 10
                    throw1_clear = True
                else:
                    num_pins -= user_input_val
                throw += 1
            elif throw == 2:
                if user_input_val == num_pins:
                    num_pins = 10
                    throw2_clear = True
                else:
                    num_pins -= user_input_val

                if throw1_clear or throw2_clear:
                    throw += 1
                else:
                    frame += 1
            elif throw == 3:
                frame += 1
    return True


def modify_loop(instance: BowlingInterface, date: str, game: int):
    if not instance.get_game(date, game):
        print(f"Game {game} on {date} not found")

    while 1:
        print("Modify> 'Frame Throw_1 Throw_2' or 'Frame Throw_1 Throw_2 Throw_3")

        while 1:
            user_input = input("Modify> ")
            user_inputs = user_input.split()
            if user_input == 'q':
                return

            frame = BowlingParser.as_num(user_inputs[0])
            if frame is None:
                print("Invalid Input: '" + user_input + "'")
                continue
            else:
                break

        data = []
        for i in user_inputs[1:]:
            data.append(BowlingParser.as_num(i))

        if not BowlingUtils.verify_frame(frame, data):
            print(f"Invalid Input: '{user_input}'\n")
        else:
            break

    for throw, value in enumerate(data, start=1):
        instance.modify_score(date, game, frame, throw, value)

    # TODO: Score Recalculation


def print_game_results(data: list):
    print(f"{' ' * 18} Frame {' ' * 56} Score")
    print("{:8} {:4} {:4}"
          .format("Date", "Game", "Scre"), end=" ")
    print("{:<6}{:<6}{:<6}{:<6}{:<6}"
          .format("1  -  ", "2  -  ", "3  -  ", "4  -  ", "5  -  "), end="")
    print("{:<6}{:<6}{:<6}{:<6}{:<9}"
          .format("6  -  ", "7  -  ", "8  -  ", "9  -  ", "10 -  -  "), end="")
    print("{:<3} {:<3} {:<3} {:<3} {:<3}"
          .format("1", "2", "3", "4", "5"), end=" ")
    print("{:<3} {:<3} {:<3} {:<3} {:<3}"
          .format("6", "7", "8", "9", "10"))

    for row in data:
        head, mid, tail = row[:3], row[3:24], row[24:]

        print("{:8} {:>4} {:>4}".format(
            BowlingDate.format_date(head[0], "%m/%d/%y"),
            head[1],
            int(head[2]) if head[2] is not None else "    "
        ), end=" ")
        prev = 0
        for i, score in enumerate(mid):
            if i % 2 == 0 and score == 10:
                print(f"x", end="  ")
                prev = 0
            elif 1 % 2 == 1 and score and score + prev == 10:
                print(f"/", end="  ")
                prev = 0
            elif not score:
                print(f"-", end="  ")
            else:
                prev = score
                print(f"{score}", end="  ")
        # for i, cumulative_score in enumerate(tail):
        #     if not cumulative_score:
        #         print(f"{'---'}", end=" ")
        #     else:
        #         print(f"{cumulative_score:>3}", end=" ")
        print()


class Validation:
    @staticmethod
    def valid_new_game(args: list) -> bool:
        if len(args) > 1:
            return False
        if len(args) == 1 and not BowlingParser.is_date(args[0]):
            return False
        return True

    @staticmethod
    def valid_modify_game(args: list) -> bool:
        if len(args) != 2:
            return False
        if not BowlingParser.is_date(args[0]) or not BowlingParser.is_num(args[1]):
            return False
        return True

    @staticmethod
    def valid_print_game(args: list) -> bool:
        if len(args) > 2:
            print("df")
            return False
        if len(args) == 2 and not BowlingParser.is_date(args[0]) and not BowlingParser.is_num(args[0]):
            return False
        if len(args) == 1 and not (BowlingParser.is_date(args[0])):
            return False
        return True

    @staticmethod
    def valid_delete_game(args: list) -> bool:
        if len(args) != 2:
            return False
        if not BowlingParser.is_date(args[0]) or not BowlingParser.is_num(args[1]):
            return False
        return True


def main(args):
    print(" Bowling Score Tracking Interface ".center(60, "="))

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    instance = BowlingInterface(
        getenv('MARIADB_USER'),
        getenv('MARIADB_PASS'),
        getenv('MARIADB_DB'),
        getenv('SPREADSHEET_ID'),
        getenv('SPREADSHEET_RANGE')
    )

    if not instance.valid:
        print("Failed to Initialize Bowling Interface")
        print("Errors", instance.err)
        print("Exiting...")
        return 1

    while 1:  # Interface loop
        user_input = input("Bowling (? for help)> ").strip()
        user_inputs = user_input.split()
        command = user_inputs[0] if user_inputs else ""
        args = user_inputs[1:]

        if command == 'q':
            print("Quitting bowling data interface...")
            break

        elif command == '?':
            if len(args) == 1:
                print_help_menu(args[0])
            else:
                print_help_menu()

        elif command == 'n':
            if not Validation.valid_new_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            if len(args) == 0:
                date = BowlingDate.today()
            else:
                date = BowlingDate.format_date(BowlingParser.as_date(args[0]))

            game_start(instance, date)

        elif command == 'm':
            if not Validation.valid_modify_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            date = BowlingDate.format_date(BowlingParser.as_date(args[0]))
            game = BowlingParser.as_num(args[1])

            modify_loop(instance, date, game)

        elif command == 'p':
            if not Validation.valid_print_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            if len(args) == 0:
                date = BowlingDate.today()

                result = instance.get_game(date)
                if not result:
                    print(f"No games played on {date}\n")
                    continue

                print_game_results(result)
            elif len(args) == 1:
                date = BowlingDate.format_date(BowlingParser.as_date(args[0]))

                result = instance.get_game(date)
                if not result:
                    print(f"No games played on {date}\n")
                    continue

                print_game_results(result)
            elif len(args) == 2:
                date = BowlingDate.format_date(BowlingParser.as_date(args[0]))
                game = BowlingParser.as_num(args[1])

                result = instance.get_game(date, game)
                if not result:
                    games_played = instance.get_games_played(date)
                    if games_played == 0:
                        print(f"No games played on {date}\n")
                    elif games_played == 1:
                        print(f"Only {games_played} game played on {date}\n")
                    else:
                        print(f"Only {games_played} games played on {date}\n")
                    continue

                print_game_results(result)
        elif command == 'd':
            if not Validation.valid_delete_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            date = BowlingDate.format_date(BowlingParser.as_date(args[0]))
            game = BowlingParser.as_num(args[1])

            instance.delete_game(date, game)

        elif command == 't':
            lists = instance.get_game(BowlingDate.format_date(BowlingParser.as_date("1/2/23")), 4)
            print(listing := BowlingUtils.calculate_scores(lists[0][3:24]))
            print(BowlingUtils.accumulate_scores(listing))
        else:
            print(f"Invalid Input: '{user_input}'")
        print()


if __name__ == '__main__':
    from sys import argv

    main(argv)
