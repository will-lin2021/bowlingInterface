"""

mainCLI.py
Written by: William Lin

Description:
Command Line Interface (CLI) for Bowling Score Tracker

"""

from BowlingInterface import BowlingInterfaceOld

from dotenv import load_dotenv
from os import getenv

SPREADSHEET_ID = None
SPREADSHEET_RANGE = None


def today(dateformat: str = "%m/%d/%y") -> str:
    from datetime import date as d
    return d.today().strftime(dateformat)


def format_date(date: str) -> str:
    from datetime import datetime as dt
    try:
        return dt.strptime(date, "%m/%d/%y").date().strftime("%m/%d/%y")
    except ValueError:
        return ""


def __print_help_menu(option: str = None):
    if option == 'n':
        print("Creates game on given date")
        print("\tusage: 'n <date>'")
    elif option == 'p':
        print("Prints game on given date")
        print("\tusage: 'p <date>'")
    elif option == 'o':
        print("Options menu for game")
        print("\tusage: 'o <option>'")
        print("\tOptions:")
        print("\t\t'm <date> <game> <frame>': modify an existing game")
    elif option == 'q':
        print("Quit Bowling Interface")
        print("\tusage: 'q'")
    else:
        print(" Interface Commands ".center(60, "="))
        print("{:1} | {}".format("n", "new game"))
        print("{:1} | {}".format("p", "print game"))
        print("{:1} | {}".format("o", "options"))
        print("{:1} | {}".format("q", "quit"))
        print("{:1} | {}".format("?", "print this menu"))
        print("Call '? <cmd>' for help with specific commands")


def main(args):
    global USER, PASS, SPREADSHEET_ID, SPREADSHEET_RANGE

    print("  Bowling Score Tracking Interface ".center(60, "="))

    if not load_dotenv("./.secrets/.env"):
        print("Failed to get .env")
        print("Exiting...")
        return

    USER = getenv('MARIADB_USER')
    PASS = getenv('MARIADB_PASS')
    DB = getenv('MARIADB_DB')
    SPREADSHEET_ID = getenv('SPREADSHEET_ID')
    SPREADSHEET_RANGE = getenv('SPREADSHEET_RANGE') if (len(args) == 1 or args[1] != "test") else getenv(
        'SPREADSHEET_TEST_RANGE')

    instance = BowlingInterfaceOld(USER, PASS, DB, SPREADSHEET_ID, SPREADSHEET_RANGE)
    if not instance.valid:
        print("Failed to get Google Sheets Interface")
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
                __print_help_menu(args[0])
            else:
                __print_help_menu()
        elif command == 'n':
            if len(args) > 1:
                print("Invalid Input: '" + user_input + "'")
                __print_help_menu(command)
            elif len(args) == 1:
                date = format_date(args[0])
                if not date:
                    print("Invalid Date Format: '" + args[0] + "'")
                else:
                    print(f" Date: {date}, Game: {instance.get_games_played(date)+1} ".center(60, "="))
                    instance.play_game(date)
            else:
                print(f" Date: {today()}, Game: {instance.get_games_played(today())+1} ".center(60, "="))
                instance.play_game(today())
        elif command == 'p':
            if len(args) > 1:
                print("Invalid Input: '" + user_input + "'")
                __print_help_menu(command)
            elif len(args) == 1:
                date = format_date(args[0])
                if not date:
                    print("Invalid Date Format: '" + args[0] + "'")
                else:
                    result = instance.print_game(date)
                    if not result:
                        print("No games played on " + args[0])
            else:
                result = instance.print_game(today())
                if not result:
                    print("No games played on " + today())
        elif command == 'o':
            if len(args) >= 1:
                if args[0] == 'm':
                    print("moddy")
            else:
                __print_help_menu(command)
        elif command == 't':
            print(instance.get_game_row(args[0]))
        else:
            print("Invalid Input: '" + user_input + "'")

        print()


if __name__ == '__main__':
    from sys import argv

    main(argv)
