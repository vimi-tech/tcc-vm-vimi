import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def index():
    nome = 'Feirascore'
    return render_template('index.html', site=nome)

@app.route('/estudantelogin')
def estudantelogin():

    return render_template('login/estudantelogin.html')

@app.route("/login")
def login():
    return render_template('login/login.html')

if __name__ == "__main__":
    app.run(debug=True)

    @app.route('/')
def index():
    return render_template('index.html')


@app.route('/estandes')
def estandes():
    return render_template('estandes.html')


@app.route('/noticias')
def noticias():
    return render_template('noticias.html')


@app.route('/localizacao')
def localizacao():
    return render_template('localizacao.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')



@app.route('/login')
def login():
  
    return render_template('login.html')

@app.route('/estudantelogin')
def estudantelogin():
   
    return render_template('estudantelogin.html')


if __name__ == '__main__':
  
    app.run(debug=True)