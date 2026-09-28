import os

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'


# ==========================================================
# CONFIGURAÇÃO DE UPLOAD
# ==========================================================

UPLOAD_FOLDER = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================================
# LISTA DOS ESTANDES
# ==========================================================

estandes_cadastrados = []


# ==========================================================
# BLUEPRINT DE AUTENTICAÇÃO
# ==========================================================

try:
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)
except Exception as e:
    print("Aviso: não foi possível carregar o auth_controller:", e)


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route("/")
def index():

    nome = 'Feirascore'

    return render_template(
        'index.html',
        site=nome
    )


# ==========================================================
# CADASTRO DE ESTANDE
# ==========================================================

@app.route(
    '/descricaoprojeto',
    methods=['GET', 'POST']
)
def pagina_descricao():

    if request.method == 'POST':

        return processar_envio_estande()

    return render_template(
        'pages/descricaoprojeto.html'
    )


@app.route(
    '/cadastrar-estande',
    methods=['POST']
)
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


    # ======================================================
    # VALIDAÇÃO DA TURMA
    # ======================================================

    if not turma or not turma.strip():

        flash(
            'Por favor, informe a sua turma!',
            'error'
        )

        return redirect(
            url_for('pagina_descricao')
        )


    turma = turma.strip()


    # ======================================================
    # VERIFICA SE A TURMA JÁ POSSUI ESTANDE
    # ======================================================

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


    # ======================================================
    # SALVA AS MÍDIAS
    # ======================================================

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

            midias_salvas.append(
                filename
            )


    # ======================================================
    # CADASTRA O ESTANDE
    # ======================================================

    estandes_cadastrados.insert(
        0,
        {
            'turma': turma,

            'nome': (
                nome_projeto
                or 'Projeto sem título'
            ),

            'resumo': resumo_projeto,

            'midias': midias_salvas
        }
    )


    flash(
        'Estande cadastrado com sucesso!',
        'success'
    )


    return redirect(
        url_for('estandes')
    )


# ==========================================================
# LISTAGEM DOS ESTANDES
# ==========================================================

@app.route('/estandes')
def estandes():

    return render_template(
        'estandes.html',
        estandes=estandes_cadastrados
    )


# ==========================================================
# LOGIN DO ESTUDANTE
# ==========================================================

@app.route('/estandelogin')
def estudantelogin():

    return render_template(
        'login/estudantelogin.html'
    )


# ==========================================================
# REGISTRO
# ==========================================================

@app.route('/register')
def register():

    return render_template(
        'login/register.html'
    )


# ==========================================================
# GERENCIAMENTO DE PROJETOS
# ==========================================================

@app.route('/projetos')
def listar_projetos():

    return render_template(
        'projetos/listar.html',
        estandes=estandes_cadastrados
    )


# ==========================================================
# PRIMEIRA TELA DE EDIÇÃO
# EDITAR NOME, TURMA E RESUMO
# ==========================================================

@app.route(
    '/projetos/editar/<int:index>',
    methods=['GET', 'POST']
)
def editar_projeto(index):

    # ------------------------------------------------------
    # VERIFICA SE O PROJETO EXISTE
    # ------------------------------------------------------

    if (
        index < 0
        or index >= len(estandes_cadastrados)
    ):

        flash(
            'Projeto não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_projetos')
        )


    estande = estandes_cadastrados[index]


    # ------------------------------------------------------
    # SE O FORMULÁRIO FOI ENVIADO
    # ------------------------------------------------------

    if request.method == 'POST':

        nome = request.form.get('nome')

        turma = request.form.get('turma')

        resumo = request.form.get('resumo')


        # --------------------------------------------------
        # VALIDA NOME
        # --------------------------------------------------

        if not nome or not nome.strip():

            flash(
                'Informe o nome do projeto!',
                'error'
            )

            return redirect(
                url_for(
                    'editar_projeto',
                    index=index
                )
            )


        # --------------------------------------------------
        # VALIDA TURMA
        # --------------------------------------------------

        if not turma or not turma.strip():

            flash(
                'Informe a turma!',
                'error'
            )

            return redirect(
                url_for(
                    'editar_projeto',
                    index=index
                )
            )


        turma = turma.strip()


        # --------------------------------------------------
        # VERIFICA SE OUTRO PROJETO JÁ USA ESSA TURMA
        # --------------------------------------------------

        turma_duplicada = any(

            i != index
            and est['turma'].lower() == turma.lower()

            for i, est in enumerate(
                estandes_cadastrados
            )

        )


        if turma_duplicada:

            flash(
                f'A turma "{turma}" já possui outro projeto cadastrado!',
                'error'
            )

            return redirect(
                url_for(
                    'editar_projeto',
                    index=index
                )
            )


        # --------------------------------------------------
        # ATUALIZA OS DADOS
        # --------------------------------------------------

        estande['nome'] = nome.strip()

        estande['turma'] = turma

        estande['resumo'] = (
            resumo.strip()
            if resumo
            else ''
        )


        flash(
            'Projeto atualizado com sucesso!',
            'success'
        )


        return redirect(
            url_for('listar_projetos')
        )


    # ------------------------------------------------------
    # ABRE A TELA DE EDIÇÃO
    # ------------------------------------------------------

    return render_template(
        'projetos/editar.html',
        estande=estande,
        index=index
    )


# ==========================================================
# SEGUNDA TELA DE EDIÇÃO
# EDITAR MÍDIAS
# ==========================================================

@app.route(
    '/projetos/editar-midias/<int:index>',
    methods=['GET', 'POST']
)
def editar_midias(index):

    # ------------------------------------------------------
    # VERIFICA SE O PROJETO EXISTE
    # ------------------------------------------------------

    if (
        index < 0
        or index >= len(estandes_cadastrados)
    ):

        flash(
            'Projeto não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_projetos')
        )


    estande = estandes_cadastrados[index]


    # ------------------------------------------------------
    # RECEBE NOVAS MÍDIAS
    # ------------------------------------------------------

    if request.method == 'POST':

        arquivos = request.files.getlist(
            'midias'
        )


        for arquivo in arquivos:

            if (
                arquivo
                and arquivo.filename
            ):

                filename = secure_filename(
                    arquivo.filename
                )


                caminho = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )


                arquivo.save(caminho)


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


    # ------------------------------------------------------
    # ABRE A TELA DE MÍDIAS
    # ------------------------------------------------------

    return render_template(
        'projetos/editar_midias.html',
        estande=estande,
        index=index
    )


# ==========================================================
# EXCLUIR PROJETO
# ==========================================================

@app.route(
    '/projetos/excluir/<int:index>',
    methods=['POST']
)
def excluir_projeto(index):

    # ------------------------------------------------------
    # VERIFICA SE EXISTE
    # ------------------------------------------------------

    if (
        index < 0
        or index >= len(estandes_cadastrados)
    ):

        flash(
            'Projeto não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_projetos')
        )


    # ------------------------------------------------------
    # REMOVE DA LISTA
    # ------------------------------------------------------

    estande = estandes_cadastrados.pop(index)


    # ------------------------------------------------------
    # REMOVE OS ARQUIVOS
    # ------------------------------------------------------

    for arquivo in estande.get(
        'midias',
        []
    ):

        caminho = os.path.join(
            app.config['UPLOAD_FOLDER'],
            arquivo
        )


        if os.path.exists(caminho):

            os.remove(caminho)


    flash(
        'Projeto excluído com sucesso!',
        'success'
    )


    return redirect(
        url_for('listar_projetos')
    )


# ==========================================================
# EXCLUIR UMA MÍDIA
# ==========================================================

@app.route(
    '/projetos/excluir-midia/<int:index>/<int:midia_index>',
    methods=['POST']
)
def excluir_midia(
    index,
    midia_index
):

    # ------------------------------------------------------
    # VERIFICA O PROJETO
    # ------------------------------------------------------

    if (
        index < 0
        or index >= len(estandes_cadastrados)
    ):

        flash(
            'Projeto não encontrado!',
            'error'
        )

        return redirect(
            url_for('listar_projetos')
        )


    estande = estandes_cadastrados[index]


    # ------------------------------------------------------
    # VERIFICA A MÍDIA
    # ------------------------------------------------------

    if (
        midia_index < 0
        or midia_index >= len(
            estande['midias']
        )
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


    # ------------------------------------------------------
    # REMOVE DA LISTA
    # ------------------------------------------------------

    arquivo = estande['midias'].pop(
        midia_index
    )


    # ------------------------------------------------------
    # REMOVE DO COMPUTADOR/SERVIDOR
    # ------------------------------------------------------

    caminho = os.path.join(
        app.config['UPLOAD_FOLDER'],
        arquivo
    )


    if os.path.exists(caminho):

        os.remove(caminho)


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


# ==========================================================
# INICIAR SERVIDOR
# ==========================================================

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


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    main()