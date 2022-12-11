"""

main.py
Written by: William Lin

Description:
Main file for running Bowling Score Tracker

"""


from BowlingInterface import BowlingInterface

from dotenv import load_dotenv
from os import getenv


SPREADSHEET_ID = None
SPREADSHEET_RANGE = None


def today(dateformat: str = "%m/%d/%y") -> str:
    from datetime import date as dt

    return dt.today().strftime(dateformat)


def __print_invalid_input(user_input, argExp: int = None, argGot: int = None) -> None:
    if not argExp and not argGot:
        print("Invalid input: '" + user_input + "'\n")
    else:
        print("Invalid number of inputs in: '" + user_input + "'")
        print("Expected " + str(argExp) + " inputs (Got " + str(argGot) + ")\n")


def main(args):
    global SPREADSHEET_ID, SPREADSHEET_RANGE

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    SPREADSHEET_ID = getenv('SPREADSHEET_ID')
    SPREADSHEET_RANGE = getenv('SPREADSHEET_RANGE')

    instance = BowlingInterface(SPREADSHEET_ID, SPREADSHEET_RANGE)
    if not instance.interface:
        print("Failed to get Google Sheets Interface")
        print("Exiting...")
        return 1

    if len(args) > 1 and args[1] == "test":
        result = instance.print_game("12/02/22")

        print(result)

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
            if len(user_inputs) > 2:  # more than 2 inputs
                __print_invalid_input(user_input, 1, len(user_inputs))
            elif len(user_inputs) == 2:  # date selected
                r_game = instance.new_game(user_inputs[1])
            elif instance.get_game(today()) != -1:  # game exists today
                print("Date already exists, use 'm' to modify date")
            else:  # game doesn't exist today
                r_game = instance.new_game(today())
                while __game_loop(r_game):
                    r_game += 1
                    break
        elif command == 'm':
            if len(user_inputs) > 2:
                __print_invalid_input(user_input)
            elif len(user_inputs) == 2:  # modify game from specific date
                r_game = instance.get_game(user_inputs[1])
                while __game_loop(r_game):
                    r_game += 1
                    break
            else:
                r_game = instance.get_game(today())
                while __game_loop(r_game):  # modify today's game
                    r_game += 1
                    break
        elif command == 'p':
            if len(user_inputs) > 2:
                __print_invalid_input(user_input)
                continue
            elif len(user_inputs) == 2:  # Print game on specific date
                result = instance.print_game(user_inputs[1])
                if not result:
                    print("No games played on " + user_inputs[1])
            else:  # Print game from today
                result = instance.print_game(today())
                if not result:
                    print("No games played on " + today())
        else:
            __print_invalid_input(user_input)
        print()


if __name__ == '__main__':
    from sys import argv
    main(argv)
