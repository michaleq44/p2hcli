# p2hcli
#### This is NOT production-ready, just for testing.
In order to use create a file `client.json`:
```json
{
  "filename_fmt": "your-song-{title}-by-{artist}-from-{album}",
  "albumname_fmt": "your-{album}-by-{artist}",
  "download_prefix": "/home/user/Music",
  "buffer_size": 131072,
  "server_address": "127.0.0.1",
  "server_port": 3571,
  "socket_timeout": 5,
  "max_results_shown": 10,
  "display_logs": false
}
```
#### Explanation:
- `"filename_fmt"` the format string for downloaded audio file names:
  - `{title}`, `{artist}` and `{album}` get replaced with their values from the song tags
- `"albumname_fmt"` the format string for download album directory names:
  - `{artist}` and `{album}` get replaced with their values from the song tags
- `"download_prefix"` the directory to which music should be downloaded
- `"buffer_size"` the size of a single chunk downloaded by the client with a socket
- `"server_address"` the server's IP address (will expand to use multiple servers at some point)
- `"server_port"` the port on which the server hosts PeerToHear
- `"socket_timeout"` the time in seconds after which a connection to the server times out
- `"max_results_shown"` the number of results search commands will show if supplied with more
- `"display_logs"` whether to display logs in the console