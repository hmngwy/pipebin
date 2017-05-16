import datetime
import errno
import os
import random
import re
import socket
import string

DOMAIN = 'localhost'
HOST = 'localhost'
SOCKET = 10000
STORE_DIR = './files'
SLUG_LEN = 8

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = (HOST, SOCKET)
sock.bind(server)
sock.listen(1)

# setup
try:
    os.makedirs(STORE_DIR)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

def log_to_stdout(message):
    time_now = str(datetime.datetime.now()).split('.')[0]
    print('[{0}] {1}'.format(time_now, message))

def path_gen(slug):
    return STORE_DIR + '/' + slug

def slug_gen(size=6, chars=string.ascii_lowercase + string.digits):
    slug = ''.join(random.choice(chars) for _ in range(size))
    if os.path.exists(path_gen(slug)):
        slug = slug_gen(6, chars)
    return slug

def save_file(slug, string):
    with open(path_gen(slug), "wb") as out:
        out.write(string)

log_to_stdout('Server has started')

while True:
    connection, client_address = sock.accept()
    connection.settimeout(10)

    try:
        log_to_stdout('Receiving message from {0}'.format(client_address))
        string = b''

        while True:
            data = connection.recv(256)
            if data:
                # saving the chunk
                string += data
            else:
                m = re.match(r'^/get ([a-zA-Z0-9]{8,})', string.encode())

                if(m):
                    slug = m.group(1)
                    with open(path_gen(slug), "rb") as out:
                        connection.sendall(out.read().encode())
                else:
                    # received end, save file, write path
                    slug = slug_gen(SLUG_LEN)
                    save_file(slug, string)
                    log_to_stdout('File with length {0} saved at {1}'.format(len(string), slug))
                    connection.sendall(('http://%s/%s\n' % (DOMAIN, slug)).encode())
                break

    finally:
        connection.close()
