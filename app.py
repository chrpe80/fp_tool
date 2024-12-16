from flask import Flask
from flask import render_template
from flask import request
from functions .all_functions import run

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        message = request.form['text-area']
        if message == "":
            return render_template("tom.html")
        else:
            path = r"C:\Users\chris\PycharmProjects\fp_tool\functions\kva-lathund-arbetsterapi.pdf"
            response = run(message, path)
            return render_template("svar.html", response=response)

@app.route('/handle_button_press/<identifier>', methods=['GET'])
def handle_button_press(identifier):
    match identifier:
        case "steg1":
            return render_template("steg1_rubriker.html")
        case "steg2":
            return render_template("steg2_rubriker.html")
        case "steg3":
            return render_template("steg3_rubriker.html")
        case "steg4":
            return render_template("steg4_rubriker.html")
        case "steg5":
            return render_template("steg5_rubriker.html")


@app.route('/warning')
def warning():
    return render_template("warning.html")



if __name__ == '__main__':
    app.run()
