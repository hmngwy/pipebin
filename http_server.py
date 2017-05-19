from flask import Flask, Response, abort, render_template
import config
import traceback
import sys
import shutil
import helpers
import os
import datetime
import pypandoc
import io

app = Flask(__name__)

@app.route("/")
def home():
    message = '{0}\n'.format(config.domain)
    message += 'a bytestring safe terminal pastebin clone\n'
    message += '\n'
    message += '# send data\n'
    message += '$ echo "simple" | nc {0} {1}\n'.format(config.domain, config.socket_port)
    message += 'http://{0}/deadbeef\n'.format(config.domain)
    message += '\n'
    message += '# read over netcat\n'
    message += '$ echo "/get deadbeef" | nc {0} {1}\n'.format(config.domain, config.socket_port)
    message += 'simple\n'
    message += '\n'
    message += '# send encrypted data as binary\n'
    message += '$ echo "sign me" | gpg --sign | nc {0} {1}\n'.format(config.domain, config.socket_port)
    message += 'http://{0}/de4dbe3f\n'.format(config.domain)
    message += '\n'
    message += '# verify or decrypt with remote gpg key in a browser\n'
    message += 'http://{0}/gpg:16CHARACTERKEYID[:<keyserver>]/d34db33f\n'.format(config.domain)
    message += '\n'
    message += "# default is sks, accepted keyservers are\n"
    for key, value in config.keyservers.items():
        message += "  {0} - {1}\n".format(key, value)
    message += "  others - send a PR at github.com/hmngwy/pipebin"

    return Response(message, mimetype='text/plain')

@app.route("/<slug>")
@app.route("/gpg:<keyid>/<slug>")
@app.route("/gpg:<keyid>:<keyserver>/<slug>")
def decrypt(slug, keyid=None, keyserver='sks', nosig=False, parse=None):

    if os.path.isfile(helpers.path_gen(slug)):
        with open(helpers.path_gen(slug), "rb") as out:
            contents = out.read()

        if keyid is None:
            is_binary = helpers.is_binary_string(contents)
            mimetype = 'octet-stream' if is_binary else 'text/plain'
            return Response(contents, mimetype=mimetype)

        elif keyid is not None:

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

                if decrypted_data.ok or decrypted_data.status == 'signature valid':
                    sig_info = "{0} {1}\nFingerprint: {2}\nTrust Level: {3}\nTrust Text: {4}\nSignature ID: {5}\n".format(decrypted_data.username, decrypted_data.key_id, decrypted_data.fingerprint, decrypted_data.trust_level, decrypted_data.trust_text, decrypted_data.signature_id)
                    sig_info += "\n----- Verification Time: " + str(datetime.datetime.now()).split('.')[0] + " -----"

                    contents = str(decrypted_data)
                    is_binary = helpers.is_binary_string(contents)

                    mimetype = 'text/plain'

                    return Response(sig_info + '\n\n' + contents, mimetype=mimetype)

                else:
                    abort(404)
            else:
                print('Key import failed')
                abort(404)


    else:
        abort(404)


if __name__ == "__main__":
    app.run(host=config.http_host)
