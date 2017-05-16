### pipebin

A terminal pastebin clone that's ok with bytestrings. Inspired by termbin (fiche) and sprunge. But I wanted one that is platform independent, in python, uses sockets for read and write, a interface for frontend parsing, and decently handles bytestrings.

  - [x] Socket server
  - [x] Read message over http
  - [x] Read message from socket
  - [ ] Decrypt with GPG public key from keyserver
  - [ ] Parse as markdown web front-end
  - [ ] AES-CBC decryption web front-end
  - [ ] Syntax highlighter web front-end

### usage

**Saving**
```
$ echo "message" | nc localhost 10000
http://localhost/deadbeef
```

**Reading**
```
$ echo "/get deadbeef" | nc localhost 10000
message
```
