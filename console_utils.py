import time
from colorama import Style, Fore

from common import *

class CmdCompleter:
    def __init__(self, options: list[str]):
        self.options = sorted(options)

    def complete(self, text, state):
        matches = [opt for opt in self.options if opt.startswith(text)]
        try:
            return matches[state]
        except IndexError:
            return None

def generate_track_search_results_print_list(results: list[tuple]) -> list[list[tuple[str, bool]]]:
    return [[(Style.DIM + f"{idx + 1}", True),
            (result[TagIndex.ARTIST], False),
            (Style.BRIGHT + Fore.GREEN + result[TagIndex.TITLE], False),
            (Style.DIM + Fore.BLUE + f"({result[TagIndex.ALBUM]})", False),
            (Style.BRIGHT + time.strftime("%M:%S", time.gmtime(result[TagIndex.DURATION])), True),
            (bytes_si(result[TagIndex.SIZE])[0], True),
            (Style.DIM + bytes_si(result[TagIndex.SIZE])[1], True),
            (Fore.RED + result[TagIndex.TYPE], False)]
           for idx, result in enumerate(results)]

def generate_album_contents_print_list(results: list[tuple]) -> list[list[tuple[str, bool]]]:
    return [[(Style.DIM + str(result[TagIndex.TRACK]), True),
            (result[TagIndex.ARTIST], False),
            (Style.BRIGHT + Fore.GREEN + result[TagIndex.TITLE], False),
            (Style.DIM + Fore.BLUE + f"({result[TagIndex.ALBUM]})", False),
            (Style.BRIGHT + time.strftime("%M:%S", time.gmtime(result[TagIndex.DURATION])), True),
            (bytes_si(result[TagIndex.SIZE])[0], True),
            (Style.DIM + bytes_si(result[TagIndex.SIZE])[1], True),
            (Fore.RED + result[TagIndex.TYPE], False)]
           for result in results]

def generate_album_search_results_print_list(results: list[tuple]) -> list[list[tuple[str, bool]]]:
    return [[(Style.DIM + f"{idx + 1}", True),
             (artist, False),
             (Style.BRIGHT + Fore.GREEN + album, False)]
           for idx, (_, artist, album, dist) in enumerate(results)]

def print_results(table: list[list[tuple[str, bool]]]):
    max_lens = [0 for _ in range(max(len(item) for item in table))]
    for item in table:
        for it, col in enumerate(item):
            col = item[it]
            max_lens[it] = max(max_lens[it], len(col[0]))
    for item in table:
        for it, col in enumerate(item):
            col = item[it]
            if col[1]:
                print(f"{col[0]:>{max_lens[it]}} ", end="")
            else:
                print(f"{col[0]:<{max_lens[it]}} ", end="")
        print()