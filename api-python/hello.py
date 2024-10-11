from flask import Flask

app = Flask(__name__)

counter = [0]

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route("/count")
def count():
    counter[0] += 1
    return f"Count is {counter[0]}"

@app.route("/json/<username>")
def json(username):
    persons = {"loosh" : "Lucian Prinz",
               "MearnsAron" : "Aaron Mearns",
               "gabrial-twiggho" : "Gabe Twiggho",
               "Milo-Coding" : "Milo Fritzen",
               "jazzyfresh" : "Jasmine Dahilig"}
    
    return f"{persons[username]}"
