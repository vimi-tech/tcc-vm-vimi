import os

from flask import Flask, render_template, request, redirect, url_for

from werkzeug.utils import secure_filename

app = Flask(__name__)



# Configuração da pasta onde os arquivos de mídia enviados serão salvos

UPLOAD_FOLDER = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# Lista global para armazenar os estandes cadastrados

estandes_cadastrados = []





@app.route("/")

def index():

    nome = 'Feirascore'

    return render_template('index.html', site=nome)





# Atualizada com suporte a POST para receber as fotos e a descrição enviadas

@app.route('/descricaoprojeto', methods=['GET', 'POST'])

def pagina_descricao():

    if request.method == 'POST':

        nome_projeto = request.form.get('nome_projeto')

        resumo_projeto = request.form.get('resumo_projeto')

       

        # Recebe a lista de arquivos (imagens/vídeos)

        arquivos = request.files.getlist('midias')

        midias_salvas = []

       

        for file in arquivos:

            if file and file.filename != '':

                filename = secure_filename(file.filename)

                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                file.save(caminho)

                midias_salvas.append(filename)



        # Adiciona o novo estande no início da lista

        estandes_cadastrados.insert(0, {

            'nome': nome_projeto,

            'resumo': resumo_projeto,

            'midias': midias_salvas

        })



        # Redireciona para a página de estandes após cadastrar

        return redirect(url_for('estandes'))



    return render_template('pages/descricaoprojeto.html')





# Atualizada para enviar os estandes cadastrados para o HTML

@app.route('/estandes')

def estandes():

    return render_template('estandes.html', estandes=estandes_cadastrados)  





@app.route('/estandelogin')

def estudantelogin():

    return render_template('login/estudantelogin.html')





@app.route("/login")

def login():

    return render_template('login/login.html')

if __name__ == "__main__":



    app.run(debug=True)