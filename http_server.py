from flask import Flask, Response, abort
import config
import gnupg
import traceback
import sys
import string
import random
import os
import shutil

app = Flask(__name__)

STORE_DIR = './files'

textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))

def slug_gen(size=6, chars=string.ascii_lowercase + string.digits):
    slug = ''.join(random.choice(chars) for _ in range(size))
    if os.path.exists(path_gen(slug)):
        slug = slug_gen(6, chars)
    return slug

def path_gen(slug):
    return STORE_DIR + '/' + slug

def create_gpg():
    gpghome = config.gpghome + '/' + slug_gen(4)
    os.makedirs(gpghome)
    open(gpghome + '/gpg.conf', 'a').close()
    os.chmod(gpghome + '/gpg.conf', 0o600)
    os.chmod(gpghome, 0o700)
    gpg = gnupg.GPG(gnupghome = gpghome)
    gpg.list_keys()
    return gpg, gpghome

@app.route("/")
def home():
    message = '0x000\n'
    message += 'a bytestring safe terminal pastebin clone\n'
    message += '\n'
    message += '# send data\n'
    message += '$ echo "simple" | nc pipeb.in 10000\n'
    message += '\n'
    message += '# send encrypted data as binary\n'
    message += '$ ls -la | openssl enc -aes-256-cbc | nc pipeb.in 10000\n'
    return Response(message, mimetype='text/plain')

@app.route("/<slug>")
def read(slug):
    with open(path_gen(slug), 'rb') as file:
        message = file.read();
        is_binary = is_binary_string(message)
    return Response(message, mimetype='octet-stream' if is_binary else 'text/plain')

@app.route("/gpg:<keyserver>:<keyid>/<slug>")
def decrypt(slug, keyserver, keyid):
    keyserver = config.keyservers[keyserver]
    gpg, gpg_homedir = create_gpg()

    try:
        import_result = gpg.recv_keys(keyserver, keyid)
    except Exception as e:
        print(traceback.format_exception(*sys.exc_info()))
        abort(500)

    if len(import_result.fingerprints)>0:
        with open(path_gen(slug), "rb") as out:
            decrypted_data = gpg.decrypt(out.read(), always_trust=True)
            delete_result = gpg.delete_keys(import_result.fingerprints[0])
            shutil.rmtree(gpg_homedir)

            print(decrypted_data.status)
            print(decrypted_data.ok)

            if decrypted_data.ok or decrypted_data.status == 'signature valid':
                message = str(decrypted_data)
                return Response(message, mimetype='text/plain')
            else:
                abort(404)
    else:
        print('key does not exist')
        abort(404)

if __name__ == "__main__":
    app.run()
