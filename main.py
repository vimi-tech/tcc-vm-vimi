import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def index():
    nome = 'Feirascore'
    return render_template('index.html', site=nome)

@app.route('/estudantelogin')
def estudantelogin():
    # Certifique-se de que o arquivo loginestudante.html está na pasta correta
    return render_template('login/estudantelogin.html')

@app.route("/login")
def login():
    return render_template('login/login.html')

if __name__ == "__main__":
    app.run(debug=True)