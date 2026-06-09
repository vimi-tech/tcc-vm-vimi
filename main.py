import os

from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route("/")
def index():
    nome = 'Feirascore'
    return render_template('index.html', site = nome)
   
# Certifique-se de que não há espaços antes do '@' e do 'def'
@app.route('/loginestudante')
def loginestudante():
    # Esse nome tem que ser idêntico ao do arquivo salvo!
    return render_template('loginestudante.html')

@app.route("/login")
def login():
    return render_template('login/login.html')

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()


