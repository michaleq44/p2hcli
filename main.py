import readline
import logging

from colorama import init, Style

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

        self.s_results = []
        self.a_results = []

    def parsecmd(self, command: str):

    @staticmethod
    def help():
        print(f'''{Style.BRIGHT}PeerToHear CLI{Style.RESET_ALL}
        Commands:
        \thelp, h - displays this help
        \tsearch, s - search for a track
        \tsearch-album, sa - search for an album
        \tview-album, a - view an album's contents
        \tdownload, d - download a track
        \tdownload-album, da - download an album
        \texit, q - exit the program
        ''')

    def search(self, arg: str):
        self.s_results = self.client.fetch_search_results(arg)

if __name__ == "__main__":
    cmdhandler = CommandHandler()
    while True:
        cmd = input(">> ")