import readline
import logging

from colorama import init

from client import ServerClient, Config, FileHandler
from console_utils import *

CONFIG_FILENAME = "client.json"

commands_short = ['h', 's', 'sa', 'a', 'd', 'da', 'q']
commands = ["help", "search", "search-album", "view-album", "download", "download-album", "exit"]
if __name__ == "__main__":
    init(autoreset=True)
    completer = CmdCompleter(commands)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    conf = Config(CONFIG_FILENAME)
    logging.basicConfig(
        level=logging.DEBUG if conf.DISPLAY_LOGS else logging.INFO,
        format='(%(asctime)s) [%(name)s]:[%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    fhandler = FileHandler(conf.PREFIX, conf)
    client = ServerClient(conf)
    while True:
        cmd = input(">> ")