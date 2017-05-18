### pipebin

A terminal pastebin clone that's ok with bytestrings. Inspired by termbin (fiche) and sprunge. But I wanted one that is platform independent, in python, uses sockets for read and write, a interface for frontend parsing, and decently handles bytestrings.

  - [x] Socket server
  - [x] Read message over http
  - [x] Read message from socket
  - [x] Decrypt with GPG key from keyserver over http
  - [ ] Parse as markdown web front-end
  - [ ] AES-CBC decryption web front-end
  - [ ] Syntax highlighter web front-end

### usage

**Writing**

Cleartext
```
$ echo "message" | nc localhost 10000
http://localhost/deadbeef
```

Encrypted and binary
```
$ echo "hide me" | gpg --sign | nc localhost 10000
http://localhost/de4dbe3f
```

**Reading**

Curl or browser
```
$ curl -s http://localhost/deadbeef
message
```

Over netcat
```
$ echo "/get deadbeef" | nc localhost 10000
message
```

**Decrypt and verify GPG signature on the browser**
```
http://localhost/gpg:16CHARACTERKEYID[:<keyserver>]/de4dbe3f
```

Where keyserver is optional or shorthand for hkp server host of public key, refer to config.py
