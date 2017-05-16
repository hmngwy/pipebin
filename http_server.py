from flask import Flask, Response
import base64

app = Flask(__name__)

STORE_DIR = './files'

textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))

def path_gen(slug):
    return STORE_DIR + '/' + slug

@app.route("/")
def home():
    string = '0x000\n'
    string += 'a bytestring safe terminal pastebin clone\n'
    string += '\n'
    string += '# send data\n'
    string += '$ echo "simple" | nc 0x000.in 10000\n'
    string += '\n'
    string += '# send encrypted data as binary\n'
    string += '$ ls -la | openssl enc -aes-256-cbc | nc 0x000.in 10000\n'
    return Response(string, mimetype='text/plain')

@app.route("/<slug>")
def read(slug):
    with open(path_gen(slug), 'rb') as file:
        string = file.read();
        is_binary = is_binary_string(string)
    return Response(string, mimetype='octet-stream' if is_binary else 'text/plain')

if __name__ == "__main__":
    app.run()
