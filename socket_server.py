import config
import datetime
import errno
import gnupg
import os
import random
import re
import socket
import string

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = (config.host, config.socket)
sock.bind(server)
sock.listen(1)

gpg = gnupg.GPG(gnupghome=config.gpghome)

# setup
try:
    os.makedirs(config.store_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

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
                    slug = slug_gen(config.slug_len)
                    save_file(slug, string)
                    log_to_stdout('File with length {0} saved at {1}'.format(len(string), slug))
                    connection.sendall(('http://%s/%s\n' % (config.domain, slug)).encode())
                break

    finally:
        connection.close()
