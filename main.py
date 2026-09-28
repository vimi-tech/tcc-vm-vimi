import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from controllers.auth_controller import auth_bp


app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

# ============================================================
# CONFIGURAÇÃO DE UPLOAD
# ============================================================

UPLOAD_FOLDER = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# BANCO TEMPORÁRIO DOS ESTANDES
# ============================================================

estandes_cadastrados = []


# ============================================================
# BLUEPRINT DE AUTENTICAÇÃO
# ============================================================

app.register_blueprint(auth_bp)


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.route("/")
def index():
    nome = 'FeiraScore'

    return render_template(
        'index.html',
        site=nome
    )


# ============================================================
# PÁGINA DE DESCRIÇÃO / CADASTRO DO PROJETO
# ============================================================

@app.route('/descricaoprojeto', methods=['GET', 'POST'])
def pagina_descricao():

    if request.method == 'POST':
        return processar_envio_estande()

    return render_template(
        'pages/descricaoprojeto.html'
    )


# ============================================================
# CADASTRAR ESTANDE
# ============================================================

@app.route('/cadastrar-estande', methods=['POST'])
def cadastrar_estande():

    return processar_envio_estande()


def processar_envio_estande():

    turma = request.form.get('turma')

    nome_projeto = (
        request.form.get('nome')
        or request.form.get('nome_projeto')
    )

    resumo_projeto = (
        request.form.get('resumo')
        or request.form.get('resumo_projeto')
    )


    # --------------------------------------------------------
    # VALIDAÇÃO DA TURMA
    # --------------------------------------------------------

    if not turma or not turma.strip():

        flash(
            'Por favor, informe a sua turma!',
            'error'
        )

        return redirect(
            url_for('pagina_descricao')
        )


    turma = turma.strip()


    # --------------------------------------------------------
    # VERIFICA SE A TURMA JÁ POSSUI UM ESTANDE
    # --------------------------------------------------------

    turma_ja_cadastrou = any(
        estande['turma'].lower() == turma.lower()
        for estande in estandes_cadastrados
    )


    if turma_ja_cadastrou:

        flash(
            f'A turma "{turma}" já possui um estande cadastrado!',
            'error'
        )

        return redirect(
            url_for('pagina_descricao')
        )


    # --------------------------------------------------------
    # SALVAR MÍDIAS
    # --------------------------------------------------------

    arquivos = request.files.getlist('midias')

    midias_salvas = []


    for file in arquivos:

        if file and file.filename != '':

            filename = secure_filename(
                file.filename
            )

            caminho = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(caminho)

            midias_salvas.append(filename)


    # --------------------------------------------------------
    # CRIAR ESTANDE
    # --------------------------------------------------------

    novo_estande = {

        'turma': turma,

        'nome': nome_projeto
        or 'Projeto sem título',

        'resumo': resumo_projeto
        or '',

        'midias': midias_salvas
    }


    estandes_cadastrados.insert(
        0,
        novo_estande
    )


    flash(
        'Estande cadastrado com sucesso!',
        'success'
    )


    return redirect(
        url_for('estandes')
    )


# ============================================================
# LISTAGEM DOS ESTANDES
# ============================================================

@app.route('/estandes')
def estandes():

    return render_template(
        'estandes.html',
        estandes=estandes_cadastrados
    )


# ============================================================
# TELA DE LISTAGEM PARA ADMINISTRAÇÃO
# ============================================================

@app.route('/listar-estandes')
def listar_estandes():

    return render_template(
        'listar_estandes.html',
        estandes=estandes_cadastrados
    )


# ============================================================
# TELA 1 DE EDIÇÃO
# EDITAR DADOS DO PROJETO
# ============================================================

@app.route(
    '/editar-estande/<int:index>',
    methods=['GET', 'POST']
)
def editar_estande(index):

    # Verifica se o estande existe

    if index < 0 or index >= len(estandes_cadastrados):

        flash(
            'Estande não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_estandes')
        )


    estande = estandes_cadastrados[index]


    # --------------------------------------------------------
    # SALVAR ALTERAÇÕES
    # --------------------------------------------------------

    if request.method == 'POST':

        turma = request.form.get('turma')
        nome = request.form.get('nome')
        resumo = request.form.get('resumo')


        if not turma or not turma.strip():

            flash(
                'A turma não pode ficar vazia!',
                'error'
            )

            return redirect(
                url_for(
                    'editar_estande',
                    index=index
                )
            )


        # Atualiza os dados

        estande['turma'] = turma.strip()

        estande['nome'] = (
            nome.strip()
            if nome
            else 'Projeto sem título'
        )

        estande['resumo'] = (
            resumo.strip()
            if resumo
            else ''
        )


        flash(
            'Dados do estande atualizados com sucesso!',
            'success'
        )


        return redirect(
            url_for('listar_estandes')
        )


    # --------------------------------------------------------
    # MOSTRAR TELA DE EDIÇÃO
    # --------------------------------------------------------

    return render_template(
        'editar_estande.html',
        estande=estande,
        index=index
    )


# ============================================================
# TELA 2 DE EDIÇÃO
# EDITAR / ADICIONAR MÍDIAS
# ============================================================

@app.route(
    '/editar-estande/<int:index>/midias',
    methods=['GET', 'POST']
)
def editar_midias(index):

    # Verifica se o estande existe

    if index < 0 or index >= len(estandes_cadastrados):

        flash(
            'Estande não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_estandes')
        )


    estande = estandes_cadastrados[index]


    # --------------------------------------------------------
    # ADICIONAR NOVAS MÍDIAS
    # --------------------------------------------------------

    if request.method == 'POST':

        arquivos = request.files.getlist('midias')


        for file in arquivos:

            if file and file.filename != '':

                filename = secure_filename(
                    file.filename
                )


                caminho = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )


                file.save(caminho)


                estande['midias'].append(
                    filename
                )


        flash(
            'Mídias atualizadas com sucesso!',
            'success'
        )


        return redirect(
            url_for(
                'editar_midias',
                index=index
            )
        )


    return render_template(
        'editar_midias.html',
        estande=estande,
        index=index
    )


# ============================================================
# EXCLUIR UMA MÍDIA
# ============================================================

@app.route(
    '/excluir-midia/<int:index>/<int:midia_index>',
    methods=['POST']
)
def excluir_midia(index, midia_index):

    # Verifica o estande

    if index < 0 or index >= len(estandes_cadastrados):

        flash(
            'Estande não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_estandes')
        )


    estande = estandes_cadastrados[index]


    # Verifica a mídia

    if (
        midia_index < 0
        or midia_index >= len(estande['midias'])
    ):

        flash(
            'Mídia não encontrada!',
            'error'
        )

        return redirect(
            url_for(
                'editar_midias',
                index=index
            )
        )


    # Pega o nome do arquivo

    filename = estande['midias'][midia_index]


    # Caminho físico do arquivo

    caminho = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )


    # Apaga o arquivo

    if os.path.exists(caminho):

        os.remove(caminho)


    # Remove da lista

    estande['midias'].pop(
        midia_index
    )


    flash(
        'Mídia excluída com sucesso!',
        'success'
    )


    return redirect(
        url_for(
            'editar_midias',
            index=index
        )
    )


# ============================================================
# LOGIN DO ESTUDANTE
# ============================================================

@app.route('/estandelogin')
def estudantelogin():

    return render_template(
        'login/estudantelogin.html'
    )


# ============================================================
# REGISTRO
# ============================================================

@app.route('/register')
def register():

    return render_template(
        'login/register.html'
    )


# ============================================================
# EXECUTAR APLICAÇÃO
# ============================================================

def main():

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )


if __name__ == "__main__":
    main()