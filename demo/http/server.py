from flask import Flask
from flask import abort, redirect, url_for
from flask import render_template as render

app_name = 'vhmmx'

app = Flask(__name__)

@app.route("/")
def index():
    return render('index.html', name = app_name)

if __name__ == "__main__":
    options = {
        'host':  '0.0.0.0',
        'debug': True,
        'port':  8000
    }

    app.run(**options)