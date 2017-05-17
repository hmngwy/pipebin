import config
import datetime
import errno
import os
import random
import re
import socket
import string

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = (config.host, config.socket)
sock.bind(server)
sock.listen(1)

# setup
try:
    os.makedirs(config.store_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise
textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))

def log_to_stdout(message):
    time_now = str(datetime.datetime.now()).split('.')[0]
    print('[{0}] {1}'.format(time_now, message))

def path_gen(slug):
    return config.store_dir + '/' + slug

def slug_gen(size=6, chars=string.ascii_lowercase + string.digits):
    slug = ''.join(random.choice(chars) for _ in range(size))
    if os.path.exists(path_gen(slug)):
        slug = slug_gen(6, chars)
    return slug

def save_file(slug, string):
    with open(path_gen(slug), "wb") as out:
        out.write(string)

log_to_stdout('Server has started at {0}:{1}'.format(config.host, config.socket))

while True:
    connection, client_address = sock.accept()
    connection.settimeout(10)

    try:
        log_to_stdout('Receiving message from {0}'.format(client_address))
        string = b''

        while True:
            data = connection.recv(256)
            if data:
                string += data
            else:
                plain = None
                if not is_binary_string(string):
                    read = re.match(r'^/get ([a-zA-Z0-9]{8,})', string.decode())

                if read:
                    slug = read.group(1)
                    with open(path_gen(slug), "rb") as out:
                        connection.sendall(out.read())
                else:
                    # received end, save file, write path
                    slug = slug_gen(config.slug_len)
                    save_file(slug, string)
                    log_to_stdout('File with length {0} saved at {1}'.format(len(string), slug))
                    connection.sendall(('http://%s/%s\n' % (config.domain, slug)).encode())
                break

    finally:
        connection.close()
