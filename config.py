import socket, json, os

class Config:
    def __init__(self, fname: str):
        self.filename = fname

        with open(self.filename, "r") as f:
            self.config = json.load(f)

        self.FILENAME_FMT = str(self.config["filename_fmt"])
        self.ALBUM_NAME_FMT = str(self.config["albumname_fmt"])
        self.PREFIX = str(self.config["prefix"])
        self.BUFFER_SIZE = int(self.config["buffer_size"])
        self.SERVER_ADDRESS = str(self.config["server_address"])
        self.SERVER_PORT = int(self.config["server_port"])
        self.SOCKET_TIMEOUT = int(self.config["socket_timeout"])
        self.MAX_NUMBER_RESULTS_SHOWN = int(self.config["max_results_shown"])

        os.makedirs(self.PREFIX, exist_ok=True)
        socket.setdefaulttimeout(self.SOCKET_TIMEOUT)