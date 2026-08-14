import readline
import logging
from traceback import format_exc

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
        self.logger = logging.getLogger(__name__)
        filetype.add_type(Opus())

        self.s_results: list[tuple] = []
        self.a_results: list[tuple] = []
        self.albumview: bool = False

    def parsecmd(self, command: str) -> bool:
        cmd = command.lower().strip().split()
        if len(cmd) == 0:
            return True
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
                    print(f"""Downloads track.
                    \tUsage: {Style.BRIGHT}download <number>{Style.RESET_ALL}
                    You acquire the number by running {Style.BRIGHT}search{Style.RESET_ALL} or {Style.BRIGHT}view-album{Style.RESET_ALL}""")
                case "download-album":
                    print(f"""Downloads albums.
                    \tUsage: {Style.BRIGHT}download-album <number>{Style.RESET_ALL}\
                    You acquire the number by running {Style.BRIGHT}search-album{Style.RESET_ALL}""")
                case _:
                    print("Invalid command")
                    return True
            return True
        args = cmd[1:]
        cmd = cmd[0]
        match cmd:
            case "search":
                self.connect_to_socket()
                self.search(" ".join(args))
            case "search-album":
                self.connect_to_socket()
                self.search(" ".join(args), album=True)
            case "view-album":
                try:
                    arg = int(args[0])
                    if arg < 1 or arg > len(self.a_results):
                        raise ValueError
                except ValueError:
                    print(f"Provide a valid number 1-{len(self.a_results)}.")
                    return True
                self.connect_to_socket()
                self.view_album(arg)
            case "download":
                todwnld = []
                try:
                    arg = int(args[0])
                    if self.albumview:
                        for idx, tags in enumerate(self.s_results):
                            if tags[TagIndex.TRACK] == arg:
                                todwnld.append(idx+1)
                        if len(todwnld) == 0:
                            raise ValueError
                    elif arg < 1 or arg > len(self.s_results):
                        raise ValueError
                    else:
                        todwnld.append(arg)
                except ValueError:
                    print(f"Provide a valid number.")
                    return True
                self.connect_to_socket()
                for t in todwnld:
                    self.download(t)
            case "download-album":
                try:
                    arg = int(args[0])
                    if arg < 1 or arg > len(self.a_results):
                        raise ValueError
                except ValueError:
                    print(f"Provide a valid number 1-{len(self.a_results)}.")
                    return True
                self.connect_to_socket()
                self.download(arg, True)
            case _:
                print("Invalid command")
                return True
        self.client.socket_close()
        return True

    def connect_to_socket(self):
        try:
            self.client.socket_connect()
        except Exception as ex:
            print(f"Failed to connect to server: {ex}")
            self.logger.debug(format_exc())

    @staticmethod
    def help():
        print(f'{Style.BRIGHT}PeerToHear CLI')
        print('''
Commands:
\thelp, h - displays this help
\tsearch, s - search for a track
\tsearch-album, sa - search for an album
\tview-album, a - view an album's contents
\tdownload, d - download a track
\tdownload-album, da - download an album
\texit, q - exit the program
To acquire detailed command info run the command without arguments.
''')

    def search(self, arg: str, album: bool = False):
        res = self.client.fetch_search_results(arg, album)
        if res is None:
            print("Failed to retrieve search results")
            return
        if album:
            self.a_results = res
            print_results(generate_album_search_results_print_list(self.a_results))
        else:
            self.s_results = [tags for tags, _ in res]
            print_results(generate_track_search_results_print_list(self.s_results))
            self.albumview = False

    def view_album(self, arg: int):
        ret = self.client.fetch_album_contents(self.a_results[arg-1][TagIndex.TITLE])
        if ret is None:
            print("Failed to retrieve album contents")
            return
        self.s_results = ret
        print_results(generate_album_contents_print_list(ret))
        self.albumview = True

    def download(self, arg: int, album: bool = False):
        ret = self.client.fetch_download((self.a_results if album else self.s_results)[arg-1]
                                         [TagIndex.TITLE if album else TagIndex.ID], album)
        if ret is None:
            print("Failed to retrieve download")
            return
        tags, data = ret
        if album:
            fname = self.fhandler.save_album(data, dict(tags))
        else:
            fname = self.fhandler.save_file(data, list(tags))
        if fname is None:
            print(f"Saving file failed.")
        else:
            print(f"Saved at: {fname}")

if __name__ == "__main__":
    _logger = logging.getLogger(__name__)
    try:
        _cmdhandler = CommandHandler()
        while True:
            _cmd = input(">> ")
            if not _cmdhandler.parsecmd(_cmd):
                break
    except KeyboardInterrupt, EOFError:
        pass
    except Exception as e:
        print(f"Client unexpectedly terminated: {e}.")
        _logger.debug(format_exc())