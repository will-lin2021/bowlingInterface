"""

mainCLI.py
Written by: William Lin

Description:
Command Line Interface (CLI) for Bowling Score Tracker

"""

from BowlingTools import Interface
from BowlingTools import GameUtils
from BowlingTools import DateUtils

from dotenv import load_dotenv
from os import getenv


def print_banner(text : str, width : int, padding : str = "="):
    text = " " + text + " "
    print(text.center(width, padding))


def print_help_menu(option: str = None):
    if option == 'n':
        print_banner("Create New Game", 30)
        print("Creates a new game on given date, or today, if date is not provided.")
        print("Usage: 'n <date optional>'")
    elif option == 'm':
        print_banner("Modify An Existing Game", 30)
        print("Modifies an existing game. ")
        print("Usage:'m <date> <game>'")
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
    elif option == 'o':
        print("Options Menu")
        print("\tusage: 'o <args>'")
        print("\targs:")
        print("\t\td: Deletes game on given date")
        print("\t\t\tusage: 'd <date> <game> <opt_args...>'")
        print("\t\t\topt_args:")
        print("\t\t\t\tforce: bypass confirmation message")
        print("\t\t\t\tnofill: delete without moving games to fill game number")
        print("\t\t\t\tall: deletes all games on given date, ignores game input")
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


def game_play(instance: Interface, date: str):
    # TODO: Deal with case when there game number is not continuous

    game_number = instance.get_games_played(date) + 1
    print(f" Date: {date}, Game Number: {game_number} ".center(60, "="))
    instance.new_game(date)

    result = game_loop(instance, date, game_number)
    if result:
        frame_data = instance.get_game(date, game_number)[0][2:23]

        frame_scores = GameUtils.calc_frame_scores(frame_data)
        accum_scores = GameUtils.accumulate_scores(frame_scores)

        for frame, score in enumerate(accum_scores, start=1):
            instance.add_score(date, game_number, frame, score)

        print("Game Complete")
    else:
        print("Game Incomplete")


def game_loop(instance: Interface, date: str, game: int) -> bool:
    frame = 1
    throw = 1
    num_pins = 10
    throw1_clear = False
    throw2_clear = False
    frame_score = []

    while frame <= 10:
        while 1:
            user_input = input(f"Frame {frame} Throw {throw} (m to modify previous score, q to quit)> ")
            user_input_val = GameUtils.score_to_num(user_input, num_pins)
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

        if throw == 1:
            frame_score = [user_input_val]
        else:
            frame_score.append(user_input_val)

        if 1 <= frame <= 9:
            if throw == 1:
                if user_input_val == 10:
                    instance.add_frame(date, game, frame, frame_score)
                    frame += 1
                    num_pins = 10
                else:
                    throw += 1
                    num_pins -= user_input_val
            else:
                instance.add_frame(date, game, frame, frame_score)
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
                    instance.add_frame(date, game, frame, frame_score)
                    throw += 1
                else:
                    instance.add_frame(date, game, frame, frame_score)
                    frame += 1
            elif throw == 3:
                instance.add_frame(date, game, frame, frame_score)
                frame += 1
    return True


def modify_loop(instance: Interface, date: str, game: int):
    if not instance.get_game(date, game):
        print(f"Game {game} on {date} not found")

    while 1:
        print("Modify> 'Frame Throw_1 Throw_2' or 'Frame Throw_1 Throw_2 Throw_3")

        while 1:
            user_input = input("Modify> ")
            user_inputs = user_input.split()
            if user_input == 'q':
                return

            frame = GameUtils.to_int(user_inputs[0])
            if frame is None:
                print("Invalid Input: '" + user_input + "'")
                continue
            else:
                break

        data = []
        for i in user_inputs[1:]:
            data.append(GameUtils.to_int(i))

        if not GameUtils.verify_frame(frame, data):
            print(f"Invalid Input: '{user_input}'\n")
        else:
            break

    for throw, value in enumerate(data, start=1):
        instance.modify_frame(date, game, frame, throw, value)

    # TODO: Score Recalculation after frame modification


def print_game_results(data: list):
    print("{:8} {:4} {:4}"
          .format("Date", "Game", "Scre"), end=" ")
    print("| ", end="")
    print("{:<4}{:<4}{:<4}{:<4}{:<4}"
          .format("1  -  ", "2  -  ", "3  -  ", "4  -  ", "5  -  "), end="")
    print("{:<4}{:<4}{:<4}{:<4}{:<7}"
          .format("6  -  ", "7  -  ", "8  -  ", "9  - ", "10  -  -  "), end="")
    print("| ", end="")
    print("{:^3} {:^3} {:^3} {:^3} {:^3} "
          .format("1", "2", "3", "4", "5"), end="")
    print("{:^3} {:^3} {:^3} {:^3} {:^3}"
          .format("6", "7", "8", "9", "10"))

    print("=" * 125)

    for row in data:
        head, mid, tail = row[:2], row[2:23], row[23:]

        print("{:8} {:>4} {:>4}".format(
            DateUtils.format_date(head[0], "%m/%d/%y"),
            head[1],
            int(tail[-1])
        ), end=" ")

        print("| ", end="")

        for frame, scores in enumerate(zip(mid[:18:2], mid[1:18:2]), start=1):
            if scores == (10, None):
                print(f"x     ", end="")
            elif sum(scores) == 10:
                if not scores[0]:
                    print(f"-  /  ", end="")
                else:
                    print(f"{scores[0]}  /  ", end="")
            else:
                if not scores[0]:
                    print(f"-  ", end="")
                else:
                    print(f"{scores[0]}  ", end="")
                if not scores[1]:
                    print(f"-  ", end="")
                else:
                    print(f"{scores[1]}  ", end="")
        prev = None
        for throw, score in enumerate(mid[18:22], start=1):
            if score is None:
                print("   ", end="")
                break

            if score == 10:
                print(f"x  ", end="")
            elif prev and prev + score == 10:
                print(f"/  ", end="")
            else:
                if not score:
                    print(f"-  ", end="")
                else:
                    print(f"{score}  ", end="")
            prev = score

        print("| ", end="")

        for i, accumulated_score in enumerate(tail):
            if not accumulated_score:
                print(f"{'---'}", end=" ")
            else:
                print(f"{accumulated_score:>3}", end=" ")
        print()


class Validation:
    @staticmethod
    def valid_new_game(args: list) -> bool:
        if len(args) > 1:
            return False
        if len(args) == 1 and not DateUtils.is_date(args[0]):
            return False
        return True

    @staticmethod
    def valid_modify_game(args: list) -> bool:
        if len(args) != 2:
            return False
        if not DateUtils.is_date(args[0]) or not GameUtils.is_int(args[1]):
            return False
        return True

    @staticmethod
    def valid_print_game(args: list) -> bool:
        if len(args) > 2:
            print("df")
            return False
        if len(args) == 2 and not DateUtils.is_date(args[0]) and not GameUtils.is_int(args[0]):
            return False
        if len(args) == 1 and not (DateUtils.is_date(args[0])):
            return False
        return True

    @staticmethod
    def valid_delete_game(args: list) -> bool:
        if len(args) != 2:
            return False
        if not DateUtils.is_date(args[0]) or not GameUtils.is_int(args[1]):
            return False
        return True


TESTING_MODE = False
DEBUG_MODE = False


def main(args):
    print_banner("Bowling Score Tracking", 60)

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    instance = Interface(
        getenv('MARIADB_USER'),
        getenv('MARIADB_PASS'),
        getenv('MARIADB_DB'),
        getenv('SPREADSHEET_ID'),
        getenv('SPREADSHEET_RANGE')
    )

    if not instance.valid:
        # TODO: Offline Mode
        # If GoogleSheetInterface errors due to internet connection issues

        print("Failed to Initialize Bowling Interface")
        print("Errors:", instance.err)
        for errors in instance.err:
            print(errors)
        print("Exiting...")
        return 1

    while 1:  # Interface loop
        # Input and Input Parsing
        user_input = input("Bowling (? for help)> ").strip()
        user_inputs = user_input.split()
        cmd = user_inputs[0] if user_inputs else ""
        args = user_inputs[1:]

        if cmd == 'q':
            print("Quitting bowling data interface...")
            break

        elif cmd == '?':
            if len(args) >= 1:
                print_help_menu(args[0])
            else:
                print_help_menu()

        elif cmd == 'n':
            if not Validation.valid_new_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                return 0

            if len(args) == 0:
                date = DateUtils.today()
            else:
                date = DateUtils.format_date(DateUtils.to_date(args[0]))

            game_play(instance, date)

        elif cmd == 'm':
            if not Validation.valid_modify_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            date = DateUtils.format_date(DateUtils.to_date(args[0]))
            game = GameUtils.to_int(args[1])

            modify_loop(instance, date, game)

        elif cmd == 'p':
            # TODO: Make a print all

            if not Validation.valid_print_game(args):
                print(f"Invalid Input: '{user_input}'\n")
                continue

            if len(args) == 0:
                date = DateUtils.today()

                result = instance.get_game(date)
                if not result:
                    print(f"No games played on {date}\n")
                    continue

                print_game_results(result)
            elif len(args) == 1:
                date = DateUtils.format_date(DateUtils.to_date(args[0]))

                result = instance.get_game(date)
                if not result:
                    print(f"No games played on {date}\n")
                    continue

                print_game_results(result)
            elif len(args) == 2:
                date = DateUtils.format_date(DateUtils.to_date(args[0]))
                game = GameUtils.to_int(args[1])

                result = instance.get_game(date, game)
                if not result:
                    games_played = instance.get_games_played(date)
                    date = DateUtils.format_date(DateUtils.to_date(args[0]), "%m/%d/%y")
                    if games_played == 0:
                        print(f"No games played on {date}\n")
                    elif games_played == 1:
                        print(f"Only {games_played} game played on {date}\n")
                    else:
                        print(f"Only {games_played} games played on {date}\n")
                    continue

                print_game_results(result)

        elif cmd == 's':
            # TODO: Statistics Menu
            # Select Overall, Year, Month, Week for data
            # Data: Spare completion percent, strike percent, average score, highest score
            # Matplotlib for graphs

            pass

        elif cmd == 'o':
            # TODO: Option Menu
            # Move delete menu here
            # Add enabling debug mode

            option_cmd = args[0]
            option_args = args[1:]

            if option_cmd == 'd':
                if not Validation.valid_delete_game(option_args):
                    print(f"Invalid Input: '{user_input}'\n")
                    continue

                date = DateUtils.format_date(DateUtils.to_date(option_args[0]))
                game = GameUtils.to_int(option_args[1])

                if instance.delete_game(date, game):
                    print(f"Deleted game {game} on {date}")
                else:
                    print("Game doesn't exist, no games deleted")
                    continue

            else:
                print(f"Invalid Input: '{user_input}'\n")
                continue

        elif cmd == 't':
            # print("Nothing is being tested at the moment")

            game_data = instance.get_game(DateUtils.format_date(DateUtils.to_date("1/25/23")))
            frame_scores = game_data[1][2:23]
            print(frame_scores)
            print(GameUtils.calc_frame_scores(frame_scores))

        else:
            print(f"Invalid Input: '{user_input}'")
        print()


if __name__ == '__main__':
    from sys import argv

    main(argv)
