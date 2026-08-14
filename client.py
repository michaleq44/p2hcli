import io
import json
import logging
import os
import random
import socket
import string
import struct
import zipfile
from traceback import format_exc

from common import *
from config import Config

class SafeFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str) and key not in kwargs:
            return f"{{{key}}}"
        return super().get_value(key, args, kwargs)

class FileHandler:
    def __init__(self, prefix: str, config: Config):
        os.makedirs(prefix, exist_ok=True)
        self.prefix = prefix
        self.conf = config

    def save_file(self, data: bytes, tagslist: list, dest: str = ".") -> str:
        if dest == '.':
            dest = self.prefix

        context_tags = {
            "title": tagslist[TagIndex.TITLE],
            "artist": tagslist[TagIndex.ARTIST],
            "album": tagslist[TagIndex.ALBUM]
        }

        formatter = SafeFormatter()
        try:
            fname = formatter.format(self.conf.FILENAME_FMT, **context_tags)+f".{tagslist[TagIndex.TYPE]}"
        except ValueError:
            fname = f"{context_tags['title']}.{tagslist[TagIndex.TYPE]}"

        with open(os.path.join(dest, fname), "wb") as f:
            f.write(data)
        return fname

    def save_album(self, data: bytes, tracktags: dict) -> str:
        firsttrack = next(iter(tracktags.values()))
        artist = firsttrack[TagIndex.ARTIST]
        album = firsttrack[TagIndex.ALBUM]
        context_tags = {
            "artist": artist,
            "album": album
        }

        formatter = SafeFormatter()
        try:
            dirname = formatter.format(self.conf.ALBUM_NAME_FMT, **context_tags)
        except ValueError:
            dirname = f"{context_tags['album']}"
        os.makedirs(dirname, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            files = []
            for info in zf.infolist():
                if not info.is_dir():
                    data = zf.read(info.filename)
                    files.append((info.filename, data))
        for fname, fdata in files:
            self.save_file(fdata, tracktags[fname], os.path.join(self.prefix, dirname))

        return dirname

class ServerClient:
    def __init__(self, config: Config):
        self.conf = config
        self.sock: socket.socket = socket.socket()
        self.logger = logging.getLogger(__name__)
        self._socket_connected = False

    def socket_connect(self):
        if self._socket_connected:
            self.socket_close()
        self.sock = socket.socket()
        self.sock.connect((self.conf.SERVER_ADDRESS, self.conf.SERVER_PORT))
        self._socket_connected = True

    def socket_close(self):
        if self._socket_connected:
            self.sock.close()
            self._socket_connected = False

    def sendrq_header(self, arg: str, rqtype: RequestType):
        tx_id = random.randint(1000, 9999)

        self.logger.debug(f"TX: {tx_id} requesting {rqtype.name}")
        rq_header = struct.pack("!BHI", rqtype, len(arg), tx_id)
        self.sock.sendall(rq_header)
        self.sock.sendall(arg.encode('utf-8'))

    def recv_json(self) -> dict | None:
        try:
            header = self.sock.recv(JSON_HEADER_SIZE)
        except Exception as e:
            header = None
            self.logger.debug(f"Exception {e}: {format_exc()}")
        if not header:
            self.logger.info("Failed retrieving response from server")
            return None

        payload_size = struct.unpack("!I", header)[0]

        raw_payload = b""
        try:
            while len(raw_payload) < payload_size:
                chunk = self.sock.recv(min(self.conf.BUFFER_SIZE, payload_size - len(raw_payload)))
                if not chunk:
                    self.logger.warning("Connection closed by server mid-transfer")
                    return None
                raw_payload += chunk
        except Exception as e:
            self.logger.debug(f"Exception {e}: {format_exc()}")
            self.logger.info("Failed retrieving information from server")

        decoded_json = json.loads(raw_payload.decode("utf-8"))

        return decoded_json

    def fetch_search_results(self, arg: str, album: bool = False) -> list[tuple] | None:
        self.sendrq_header(arg, RequestType.SEARCH_ALBUM if album else RequestType.SEARCH)

        received = self.recv_json()
        if received is None:
            return None

        final_list = [tuple(item) for item in received]
        return final_list

    def fetch_album_contents(self, arg: str):
        self.sendrq_header(arg, RequestType.SHOW_ALBUM)

        received = self.recv_json()
        if received is None:
            return None

        final_list = [tuple(item) for item in received]
        return final_list

    def fetch_download(self, arg: str, album: bool = False) -> tuple[dict, bytes] | None:
        self.sendrq_header(arg, RequestType.DOWNLOAD_ALBUM if album else RequestType.DOWNLOAD)

        header = self.sock.recv(DOWNLOAD_HEADER_SIZE)
        if not header:
            self.logger.debug("Connection closed by server")
            return None

        error, fsize, tagsize = struct.unpack("!BQI", header)
        if not error:
            return None
        tagslist = json.loads(self.sock.recv(tagsize).decode("utf-8"))

        raw_payload = b""
        while len(raw_payload) < fsize:
            chunk = self.sock.recv(min(self.conf.BUFFER_SIZE, fsize - len(raw_payload)))
            if not chunk:
                raise ConnectionError("Connection closed by server mid-transfer")
            raw_payload += chunk

        return tagslist, raw_payload