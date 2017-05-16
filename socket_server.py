import datetime
import errno
import os
import random
import socket
import string
import time

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
    time_now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S')
    print('[%s] %s' % (time_now, message))

def path_gen(slug):
    return STORE_DIR + '/' + slug

def slug_gen(size=6, chars=string.ascii_lowercase + string.digits):
    slug = ''.join(random.choice(chars) for _ in range(size))
    if os.path.exists(path_gen(slug)):
        slug = slug_gen(6, chars)
    return slug

log_to_stdout('Server has started')

while True:
    connection, client_address = sock.accept()
    connection.settimeout(10)

    try:
        log_to_stdout('Receiving message from %s' % client_address)
        string = b''

        while True:
            data = connection.recv(16)
            if data:
                # saving the chunk
                string += data
            else:
                # received end, save file, write path
                slug = slug_gen(SLUG_LEN)
                with open(path_gen(slug), "wb") as out:
                    out.write(string)
                log_to_stdout('File with length %d saved at %s' % (len(string), slug))
                connection.sendall(('http://%s/%s\n' % (DOMAIN, slug)).encode())
                break

    finally:
        connection.close()
