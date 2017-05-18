import config
import errno
import os
import re
import socket
import helpers

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = (config.socket_host, config.socket_port)
sock.bind(server)
sock.listen(1)

# setup
try:
    os.makedirs(config.store_dir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

helpers.log_to_stdout('Server has started at {0}:{1}'.format(config.socket_host, config.socket_port))

while True:
    connection, client_address = sock.accept()
    connection.settimeout(10)

    try:
        helpers.log_to_stdout('Receiving message from {0}'.format(client_address))
        string = b''

        while True:
            data = connection.recv(256)
            if data:
                string += data
            else:
                read = None
                if not helpers.is_binary_string(string):
                    read = re.match(r'^/get ([a-zA-Z0-9]{8,})', string.decode())

                if read:
                    slug = read.group(1)
                    with open(helpers.helpers.path_gen(slug), "rb") as out:
                        connection.sendall(out.read())
                else:
                    # received end, save file, write path
                    slug = helpers.slug_gen(config.slug_len)
                    helpers.save_file(slug, string)
                    helpers.log_to_stdout('File with length {0} saved at {1}'.format(len(string), slug))
                    connection.sendall(('http://%s/%s\n' % (config.domain, slug)).encode())
                break

    finally:
        connection.close()
