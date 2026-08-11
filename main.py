import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

estandes_cadastrados = []


@app.route("/")
def index():
    nome = 'Feirascore'
    return render_template('index.html', site=nome)


@app.route('/descricaoprojeto', methods=['GET', 'POST'])
def pagina_descricao():
    if request.method == 'POST':
        return processar_envio_estande()

    return render_template('pages/descricaoprojeto.html')


@app.route('/cadastrar-estande', methods=['POST'])
def cadastrar_estande():
    return processar_envio_estande()


def processar_envio_estande():
    turma = request.form.get('turma')
    nome_projeto = request.form.get('nome') or request.form.get('nome_projeto')
    resumo_projeto = request.form.get('resumo') or request.form.get('resumo_projeto')
    
    # 1. Validação de campos obrigatórios
    if not turma or not turma.strip():
        flash('Por favor, informe a sua turma!', 'error')
        return redirect(url_for('pagina_descricao'))

    turma = turma.strip()

    # ------------------------------------------------------------------
    # VALIDAÇÃO: Bloqueia se a TURMA já cadastrou algum projeto
    # ------------------------------------------------------------------
    turma_ja_cadastrou = any(
        estande['turma'].lower() == turma.lower() 
        for estande in estandes_cadastrados
    )

    if turma_ja_cadastrou:
        flash(f'A turma "{turma}" já possui um estande cadastrado!', 'error')
        return redirect(url_for('pagina_descricao'))

    # 2. Salva as mídias se a turma for nova
    arquivos = request.files.getlist('midias')
    midias_salvas = []
    
    for file in arquivos:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)
            midias_salvas.append(filename)

    # 3. Adiciona o estande associado à turma
    estandes_cadastrados.insert(0, {
        'turma': turma,
        'nome': nome_projeto or 'Projeto sem título',
        'resumo': resumo_projeto,
        'midias': midias_salvas
    })
    
    flash('Estande cadastrado com sucesso!', 'success')
    return redirect(url_for('estandes'))


@app.route('/estandes')
def estandes():
    return render_template('estandes.html', estandes=estandes_cadastrados)  


@app.route('/estandelogin')
def estudantelogin():
    return render_template('login/estudantelogin.html')


@app.route("/login")
def login():
    return render_template('login/login.html')

def main():
    app.run(host="0.0.0.0", port = int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    main()