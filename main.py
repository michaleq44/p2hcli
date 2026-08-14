import readline
import logging

import filetype
from colorama import init, Style
from filetype import add_type

from client import ServerClient, Config, FileHandler
from console_utils import *

CONFIG_FILENAME = "client.json"

commands_short = {'h': "help", 's': "search", 'sa': "search-album", 'a': "view-album", 'd': "download",
                  'da': "download-album", 'q': "exit"}
commands = ["help", "search", "search-album", "view-album", "download", "download-album", "exit"]

class CommandHandler:
    def __init__(self):
        init(autoreset=True)
        self.completer = CmdCompleter(commands)
        readline.set_completer(self.completer.complete)
        readline.parse_and_bind("tab: complete")

        self.conf = Config(CONFIG_FILENAME)
        logging.basicConfig(
            level=logging.DEBUG if self.conf.DISPLAY_LOGS else logging.INFO,
            format='(%(asctime)s) [%(name)s]:[%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
            ]
        )
        self.fhandler = FileHandler(self.conf.PREFIX, self.conf)
        self.client = ServerClient(self.conf)
        filetype.add_type(Opus())

        self.s_results = []
        self.a_results = []

    def parsecmd(self, command: str) -> bool:
        cmd = command.lower().strip().split()
        if len(cmd) == 0:
            pass
        elif cmd[0] in commands_short:
            cmd[0] = commands_short[cmd[0]]
        if cmd[0] == "help":
            self.help()
            return True
        elif cmd[0] == "exit":
            return False
        if len(cmd) == 1:
            match cmd[0]:
                case "search":
                    print(f"Searches for a track.\n\tUsage: {Style.BRIGHT}search <query>{Style.RESET_ALL}")
                case "search-album":
                    print(f"Searches for an album.\n\tUsage: {Style.BRIGHT}search-album <query>{Style.RESET_ALL}")
                case "view-album":
                    print(f"""Displays tracks in selected album.\n
                    \tUsage: {Style.BRIGHT}view-album <number>{Style.RESET_ALL}\n
                    You acquire the number by running {Style.BRIGHT}search-album{Style.RESET_ALL}""")
                case "download":
                    print(f"""Downloads track.\n
                    \tUsage: {Style.BRIGHT}download <number>{Style.RESET_ALL}\n
                    You acquire the number by running {Style.BRIGHT}search{Style.RESET_ALL} or {Style.BRIGHT}view-album{Style.RESET_ALL}""")
                case "download-album":
                    print(f"""Downloads albums.\n
                    \tUsage: {Style.BRIGHT}download-album <number>{Style.RESET_ALL}\n
                    You acquire the number by running {Style.BRIGHT}search-album{Style.RESET_ALL}""")
                case _:
                    print("Invalid command")
                    return True
        args = cmd[1:]
        cmd = cmd[0]
        match cmd:
            case "search":
                self.search(" ".join(args))

        return True

    @staticmethod
    def help():
        print(f'''{Style.BRIGHT}PeerToHear CLI{Style.RESET_ALL}\n
        Commands:\n
        \thelp, h - displays this help\n
        \tsearch, s - search for a track\n
        \tsearch-album, sa - search for an album\n
        \tview-album, a - view an album's contents\n
        \tdownload, d - download a track\n
        \tdownload-album, da - download an album\n
        \texit, q - exit the program\n
        To acquire detailed command info run the command without arguments.
        ''')

    def search(self, arg: str):
        res = self.client.fetch_search_results(arg)
        if res is None:
            print("Failed to retrieve search results")
            return
        print_results(generate_track_search_results_print_list(self.s_results))

if __name__ == "__main__":
    _cmdhandler = CommandHandler()
    while True:
        _cmd = input(">> ")
