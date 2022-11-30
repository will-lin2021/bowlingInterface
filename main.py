from BowlingInterface import BowlingInterface

from datetime import date
from dotenv import load_dotenv
from os import getenv

SPREADSHEET_ID = None
SPREADSHEET_RANGE = None


def today() -> str:
    return date.today().strftime("%m/%d/%y")


def print_invalid_input(user_input, argExp: int = None, argGot: int = None) -> None:
    if not argExp and not argGot:
        print("Invalid input: '" + user_input + "'\n")
    else:
        print("Invalid number of inputs in: '" + user_input + "'")
        print("Expected " + str(argExp) + " inputs (Got " + str(argGot) + ")\n")


def game_loop(row: int):
    if row == 30:
        return False
    while 1:
        print(row)
        return True


def main(args):
    global SPREADSHEET_ID, SPREADSHEET_RANGE

    if not load_dotenv():
        print("Failed to get .env")
        print("Exiting...")
        return
    SPREADSHEET_ID = getenv('SPREADSHEET_ID')

    SPREADSHEET_RANGE = 'Bowling Data'
    SPREADSHEET_RANGE = 'Testing Grounds'

    instance = BowlingInterface(SPREADSHEET_ID, SPREADSHEET_RANGE)
    if not instance.sheet:
        print("Failed to get Google Sheets Interface")
        print("Exiting...")
        return 1

    if len(args) > 1 and args[1] == "test":
        instance.new_game("11/23/22")
        return

    while 1:  # Interface loop
        print("Bowling Interface Commands")
        print("{0:^7} | {1:10} | {2}".format("Command", "Inputs", "Function"))
        print("{0:^7} | {1:10} | {2}".format("p", "date", "Print game from date (default: today)"))
        print("{0:^7} | {1:10} | {2}".format("m", "date", "Modify existing game"))
        print("{0:^7} | {1:10} | {2}".format("n", "None", "Starts a new game today"))
        print("{0:^7} | {1:10} | {2}".format("q", "None", "Quit interface"))

        user_input = input("Bowling> ")
        user_inputs = user_input.split(" ")
        command = user_inputs[0]
        if command == 'q':
            print("Quitting bowling data interface...")
            break
        elif command == 'n':
            if len(user_inputs) > 2:
                print_invalid_input(user_input, 1, len(user_inputs))
            elif len(user_inputs) == 2:
                r_game = instance.new_game(user_inputs[1])
                game_loop(r_game)
            elif instance.get_date(today()) != -1:  # game exists today
                print("Date already exists, use 'm' to modify date")
            else:  # game doesn't exist today
                r_game = instance.new_game(today())
                while game_loop(r_game):
                    r_game += 1
        elif command == 'm':
            if len(user_inputs) > 2:
                print_invalid_input(user_input)
            elif len(user_inputs) == 2:  # modify game from specific date
                r_game = instance.get_date(user_inputs[1])
                while game_loop(r_game):
                    r_game += 1
            else:
                r_game = instance.get_date(today())
                while game_loop(r_game):  # modify today's game
                    r_game += 1
        elif command == 'p':
            if len(user_inputs) > 2:
                print_invalid_input(user_input)
                continue
            elif len(user_inputs) == 2:  # Print game on specific date
                result = instance.print_game(user_inputs[1])
                if result == 1:
                    print("No games played on " + user_inputs[1])
            else:  # Print game from today
                result = instance.print_game(today())
                if result == 1:
                    print("No games played on " + today())
        else:
            print_invalid_input(user_input)
        print()


if __name__ == '__main__':
    from sys import argv
    main(argv)
