import argparse
import os
from flask import Flask, request, send_from_directory, redirect
from flask_httpauth import HTTPBasicAuth
import urllib

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if username == app.config['username'] and password == app.config['password']:
        return username


@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return redirect('/', code=302)

    file = request.files['file']

    if file.filename == '':
        return redirect('/', code=302)

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads', file.filename)
    file.save(filename)

    return redirect('/', code=302)


@app.route('/', defaults={'file_or_folder': ''}, methods=['GET'])
@app.route('/<path:file_or_folder>', methods=['GET'])
@auth.login_required
def home_page(file_or_folder):
    if os.path.isfile(os.path.join(os.getcwd(), file_or_folder)):
        return send_from_directory(os.getcwd(), file_or_folder, as_attachment=True)

    file_list_html = ''

    file_list = os.listdir(os.path.join(os.getcwd(), file_or_folder))

    for filename in file_list:
        file_href = file_display_name = filename

        if os.path.isdir(filename):
            file_display_name = filename + '/'
            file_href = file_href + '/'
        if os.path.islink(filename):
            file_display_name = filename + '@'

        file_list_html = file_list_html + '<li><a href=\'{}\'>{}</a></li>\n'.format(
            urllib.parse.quote(os.path.join('/', file_or_folder, file_href)),
            file_display_name
        )

    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Microsoft-HTTPAPI/2.0</title>
            <link href='data:image/x-icon;base64,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' rel='icon' type='image/x-icon' />
            <style>
            body {{ background-color: #484538; color: #06ACCA; }}
            input[type=submit], input[type=file]::file-selector-button {{
              background-color: #52489C;
              border: none;
              color: white;
              padding: 7px 20px;
              text-decoration: none;
              margin: 4px 2px;
              cursor: pointer;
            }}
            a {{ text-decoration: none; color:#06ACCA; }}
            a:visited {{ text-decoration: none; color:#06ACCA; }}
            a:hover {{ text-decoration: none; color:#06ACCA; }}
            a:focus {{ text-decoration: none; color:#06ACCA; }}
            a:hover, a:active {{ text-decoration: none; color:#06ACCA }}
            h2 {{ color:#06ACCA; }}
            </style>
        </head>
        <body>
            <h2>Directory listing for {}</h2>
            <hr>
            <form ENCTYPE='multipart/form-data' method='post' action='/upload'>
                <input name='file' type='file'/>
                <input type='submit' value='upload'/>
            </form>
            <hr>
            <ul>
                {}
            </ul>
            <hr>
        </body>
        </html>
    """.format(request.path, file_list_html).encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Up Up Down Down', description='Python Flask file server')
    parser.add_argument('-u', '--username', required=False, type=str, action='store', dest='username',
                        help='Basic auth username', default='qqq')
    parser.add_argument('-p', '--password', required=False, type=str, action='store', dest='password',
                        help='Basic auth password', default='www')
    parser.add_argument('-o', '--port', required=False, type=int, action='store', dest='port',
                        help="HTTP server port", default=8000)
    args = parser.parse_args()

    app.config['username'] = args.username
    app.config['password'] = args.password
    app.run(ssl_context='adhoc', debug=False, host='0.0.0.0', port=args.port)

