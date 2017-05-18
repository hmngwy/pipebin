from flask import Flask, Response, abort
import config
import traceback
import sys
import shutil
import helpers
import os
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    message = '0x000\n'
    message += 'a bytestring safe terminal pastebin clone\n'
    message += '\n'
    message += '# send data\n'
    message += '$ echo "simple" | nc pipebin.org 10000\n'
    message += '\n'
    message += '# send encrypted data as binary\n'
    message += '$ ls -la | openssl enc -aes-256-cbc | nc pipebin.org 10000\n'
    return Response(message, mimetype='text/plain')

@app.route("/<slug>")
def read(slug):
    if os.path.isfile(helpers.path_gen(slug)):
        with open(helpers.path_gen(slug), 'rb') as file:
            message = file.read();
            is_binary = helpers.is_binary_string(message)
        return Response(message, mimetype='octet-stream' if is_binary else 'text/plain')
    else:
        abort(404)

@app.route("/gpg:<action>:<keyserver>:<keyid>/<slug>")
def decrypt(slug, keyserver, action, keyid):
    try:
        keyserver_full = config.keyservers[keyserver]
    except KeyError:
        abort(404)

    gpg, gpg_homedir = helpers.create_gpg()

    try:
        import_result = gpg.recv_keys(keyserver_full, keyid)
    except Exception as e:
        print(str(e))
        abort(404)

    if len(import_result.fingerprints)>0:
        with open(helpers.path_gen(slug), "rb") as out:
            decrypted_data = gpg.decrypt(out.read(), always_trust=True)
            delete_result = gpg.delete_keys(import_result.fingerprints[0])
            shutil.rmtree(gpg_homedir)

            print(decrypted_data.status)
            print(decrypted_data.ok)

            if decrypted_data.ok or decrypted_data.status == 'signature valid':
                if action == 'decrypt':
                    message = str(decrypted_data)
                    return Response(message, mimetype='text/plain')
                elif action == 'verify':
                    message = "{0} {1}\nFingerprint: {2}\nTrust Level: {3}\nTrust Text: {4}\nSignature ID: {5}\n".format(decrypted_data.username, decrypted_data.key_id, decrypted_data.fingerprint, decrypted_data.trust_level, decrypted_data.trust_text, decrypted_data.signature_id)
                    #message += "\nWithout Signature Data: http://{0}/gpg:{1}:decrypt:{2}/{3}\n".format(config.domain, keyserver, keyid, slug)
                    message += "\n----- Verification Time: " + str(datetime.datetime.now()).split('.')[0] + " -----\n"
                    message += "\n" + str(decrypted_data)
                    return Response(message, mimetype='text/plain')
                else:
                    abort(404)
            else:
                abort(404)
    else:
        print('Key import failed')
        abort(404)

if __name__ == "__main__":
    app.run(host=config.http_host)
