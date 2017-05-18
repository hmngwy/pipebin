import datetime
import config
import random
import string
import os
import gnupg
import shutil

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

def create_gpg():
    gpghome = config.gpghome + '/' + slug_gen(4)
    os.makedirs(gpghome)
    open(gpghome + '/gpg.conf', 'a').close()
    os.chmod(gpghome + '/gpg.conf', 0o600)
    os.chmod(gpghome, 0o700)
    gpg = gnupg.GPG(gnupghome = gpghome, gpgbinary = str(shutil.which('gpg')))
    gpg.list_keys()
    return gpg, gpghome
