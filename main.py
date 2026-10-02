import html
import os
import traceback
import uuid

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session
)
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Em produção defina a variável de ambiente SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')


# ==========================================================
# CONFIGURAÇÃO DE UPLOAD
# ==========================================================

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================================
# DADOS EM MEMÓRIA
# ==========================================================

# Cada estande: {'id', 'turma', 'nome', 'resumo', 'midias'}
estandes_cadastrados = []

# As 8 perguntas da votação: o visitante escolhe UM projeto em cada uma
PERGUNTAS_VOTACAO = [
    {"titulo": "Tema da feira",      "pergunta": "Qual projeto se relaciona completamente com o tema da feira?"},
    {"titulo": "Melhor decoração",   "pergunta": "Qual teve a melhor decoração?"},
    {"titulo": "Melhor didática",    "pergunta": "Qual teve a melhor didática?"},
    {"titulo": "Mais relevante",     "pergunta": "Qual foi o mais relevante?"},
    {"titulo": "Mais interessante",  "pergunta": "Qual foi o mais interessante?"},
    {"titulo": "Mais criativo",      "pergunta": "Qual foi o mais criativo?"},
    {"titulo": "Mais organizado",    "pergunta": "Qual foi o mais organizado?"},
    {"titulo": "Melhor explicação",  "pergunta": "Qual teve a melhor explicação?"},
]

# Votos: um contador por pergunta -> votos[i] = {id_do_estande: quantidade}
votos = [{} for _ in PERGUNTAS_VOTACAO]

# Quantas pessoas já enviaram a cédula
contagem = {"votantes": 0}


def buscar_estande(estande_id):
    for estande in estandes_cadastrados:
        if estande['id'] == estande_id:
            return estande
    return None


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
    return render_template('index.html', site='Feirascore')


# ==========================================================
# CADASTRO DE ESTANDE
# ==========================================================

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

    if not turma or not turma.strip():
        flash('Por favor, informe a sua turma!', 'error')
        return redirect(url_for('pagina_descricao'))

    turma = turma.strip()

    if any(e['turma'].lower() == turma.lower() for e in estandes_cadastrados):
        flash(f'A turma "{turma}" já possui um estande cadastrado!', 'error')
        return redirect(url_for('pagina_descricao'))

    midias_salvas = []
    for file in request.files.getlist('midias'):
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            midias_salvas.append(filename)

    estandes_cadastrados.insert(0, {
        'id': uuid.uuid4().hex,          # identificador fixo (usado na votação)
        'turma': turma,
        'nome': nome_projeto or 'Projeto sem título',
        'resumo': resumo_projeto,
        'midias': midias_salvas,
    })

    flash('Estande cadastrado com sucesso!', 'success')
    return redirect(url_for('estandes'))


# ==========================================================
# LISTAGEM DOS ESTANDES
# ==========================================================

@app.route('/estandes')
def estandes():
    return render_template('estandes.html', estandes=estandes_cadastrados)


# ==========================================================
# LOGIN DO ESTUDANTE / REGISTRO
# ==========================================================

@app.route('/estandelogin')
def estudantelogin():
    return render_template('login/estudantelogin.html')


@app.route('/register')
def register():
    return render_template('login/register.html')


# ==========================================================
# GERENCIAMENTO DE PROJETOS
# ==========================================================

@app.route('/projetos')
def listar_projetos():
    return render_template('projetos/listar.html', estandes=estandes_cadastrados)


# ----------------------------------------------------------
# EDITAR PROJETO
# (no seu arquivo esta função estava SEM o @app.route e o
#  "def", o que quebrava o programa inteiro)
# ----------------------------------------------------------

@app.route('/projetos/editar/<int:index>', methods=['GET', 'POST'])
def editar_projeto(index):

    if index < 0 or index >= len(estandes_cadastrados):
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    estande = estandes_cadastrados[index]

    if request.method == 'POST':
        nome = request.form.get('nome')
        turma = request.form.get('turma')
        resumo = request.form.get('resumo')

        if not nome or not nome.strip():
            flash('Informe o nome do projeto!', 'error')
            return redirect(url_for('editar_projeto', index=index))

        if not turma or not turma.strip():
            flash('Informe a turma!', 'error')
            return redirect(url_for('editar_projeto', index=index))

        turma = turma.strip()

        turma_duplicada = any(
            i != index and est['turma'].lower() == turma.lower()
            for i, est in enumerate(estandes_cadastrados)
        )
        if turma_duplicada:
            flash(f'A turma "{turma}" já possui outro projeto cadastrado!', 'error')
            return redirect(url_for('editar_projeto', index=index))

        estande['nome'] = nome.strip()
        estande['turma'] = turma
        estande['resumo'] = resumo.strip() if resumo else ''

        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_projetos'))

    return render_template('projetos/editar.html', estande=estande, index=index)


# ----------------------------------------------------------
# EDITAR MÍDIAS
# ----------------------------------------------------------

@app.route('/projetos/editar-midias/<int:index>', methods=['GET', 'POST'])
def editar_midias(index):

    if index < 0 or index >= len(estandes_cadastrados):
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    estande = estandes_cadastrados[index]

    if request.method == 'POST':
        for arquivo in request.files.getlist('midias'):
            if arquivo and arquivo.filename:
                filename = secure_filename(arquivo.filename)
                arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                estande['midias'].append(filename)

        flash('Mídias atualizadas com sucesso!', 'success')
        return redirect(url_for('editar_midias', index=index))

    return render_template('projetos/editar_midias.html', estande=estande, index=index)


# ----------------------------------------------------------
# EXCLUIR PROJETO
# ----------------------------------------------------------

@app.route('/projetos/excluir/<int:index>', methods=['POST'])
def excluir_projeto(index):

    if index < 0 or index >= len(estandes_cadastrados):
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    estande = estandes_cadastrados.pop(index)

    # apaga também os votos desse projeto
    for contador in votos:
        contador.pop(estande['id'], None)

    for arquivo in estande.get('midias', []):
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)

    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('listar_projetos'))


# ----------------------------------------------------------
# EXCLUIR UMA MÍDIA
# ----------------------------------------------------------

@app.route('/projetos/excluir-midia/<int:index>/<int:midia_index>', methods=['POST'])
def excluir_midia(index, midia_index):

    if index < 0 or index >= len(estandes_cadastrados):
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    estande = estandes_cadastrados[index]

    if midia_index < 0 or midia_index >= len(estande['midias']):
        flash('Mídia não encontrada!', 'error')
        return redirect(url_for('editar_midias', index=index))

    arquivo = estande['midias'].pop(midia_index)

    caminho = os.path.join(app.config['UPLOAD_FOLDER'], arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)

    flash('Mídia excluída com sucesso!', 'success')
    return redirect(url_for('editar_midias', index=index))


# ==========================================================
# VOTAÇÃO  (uma cédula com 8 perguntas, 1 projeto por pergunta)
# ==========================================================

def garantir_ids():
    for e in estandes_cadastrados:
        e.setdefault('id', uuid.uuid4().hex)


def primeira_sem_resposta(respostas):
    for i in range(1, len(PERGUNTAS_VOTACAO) + 1):
        if str(i) not in respostas:
            return i
    return len(PERGUNTAS_VOTACAO)


@app.route('/votacao')
def iniciar_votacao():
    """Se houver projetos e a pessoa ainda não votou, começa as perguntas.
    Senão mostra 'nenhum projeto disponível' ou 'você já votou'."""
    garantir_ids()

    if estandes_cadastrados and not session.get('votou'):
        return redirect(url_for(
            'exibir_pergunta',
            numero=primeira_sem_resposta(session.get('respostas', {}))
        ))

    return render_template(
        'votacao/lista.html',
        estandes=estandes_cadastrados,
        ja_votou=session.get('votou', False),
    )


@app.route('/votacao/pergunta/<int:numero>', methods=['GET', 'POST'])
def exibir_pergunta(numero):
    """Uma pergunta por tela. A resposta de cada tela fica na sessão
    e os votos só são contados ao finalizar a pergunta 8."""
    garantir_ids()
    total = len(PERGUNTAS_VOTACAO)

    if not estandes_cadastrados:
        flash('Não há nenhum projeto disponível para votação.', 'error')
        return redirect(url_for('iniciar_votacao'))

    if session.get('votou'):
        flash('Você já votou. Obrigado pela participação!', 'error')
        return redirect(url_for('iniciar_votacao'))

    if numero < 1 or numero > total:
        return redirect(url_for('exibir_pergunta', numero=1))

    ids_validos = {e['id'] for e in estandes_cadastrados}
    respostas = {
        k: v for k, v in session.get('respostas', {}).items()
        if v in ids_validos
    }

    if request.method == 'POST':
        escolha = request.form.get('estande')
        if escolha not in ids_validos:
            flash('Escolha um projeto para continuar.', 'error')
            return redirect(url_for('exibir_pergunta', numero=numero))

        respostas[str(numero)] = escolha
        session['respostas'] = respostas

        if numero < total:
            return redirect(url_for('exibir_pergunta', numero=numero + 1))

        # última pergunta: confere se todas foram respondidas e registra
        if len(respostas) < total:
            return redirect(url_for(
                'exibir_pergunta', numero=primeira_sem_resposta(respostas)
            ))

        for i in range(total):
            escolhido = respostas[str(i + 1)]
            votos[i][escolhido] = votos[i].get(escolhido, 0) + 1
        contagem['votantes'] += 1
        session['votou'] = True
        session.pop('respostas', None)

        flash('Voto registrado com sucesso! Obrigado pela participação.', 'success')
        return redirect(url_for('iniciar_votacao'))

    # GET: não deixa pular perguntas
    faltando = primeira_sem_resposta(respostas)
    if numero > faltando:
        return redirect(url_for('exibir_pergunta', numero=faltando))

    return render_template(
        'votacao/etapa.html',
        numero=numero,
        total=total,
        pergunta=PERGUNTAS_VOTACAO[numero - 1],
        estandes=estandes_cadastrados,
        escolhida=respostas.get(str(numero)),
    )


@app.route('/ranking')
def ranking():
    """Vencedor de cada pergunta + classificação geral (soma dos votos)."""
    garantir_ids()
    categorias = []
    total_geral = {e['id']: 0 for e in estandes_cadastrados}

    for i, item in enumerate(PERGUNTAS_VOTACAO):
        linhas = []
        for e in estandes_cadastrados:
            qtd = votos[i].get(e['id'], 0)
            total_geral[e['id']] += qtd
            linhas.append({'estande': e, 'qtd': qtd})
        linhas.sort(key=lambda l: l['qtd'], reverse=True)
        categorias.append({
            'titulo': item['titulo'],
            'pergunta': item['pergunta'],
            'linhas': linhas,
            'maior': linhas[0]['qtd'] if linhas else 0,
        })

    geral = sorted(
        ({'estande': e, 'qtd': total_geral[e['id']]} for e in estandes_cadastrados),
        key=lambda l: l['qtd'], reverse=True,
    )

    return render_template(
        'votacao/ranking.html',
        categorias=categorias,
        geral=geral,
        votantes=contagem['votantes'],
    )


# ==========================================================
# DIAGNÓSTICO: com a variável MOSTRAR_ERROS=1 o erro 500 mostra
# o motivo na própria página (remova a variável depois de resolver)
# ==========================================================

@app.errorhandler(500)
def erro_interno(e):
    if os.environ.get('MOSTRAR_ERROS') == '1':
        original = getattr(e, 'original_exception', None) or e
        texto = ''.join(traceback.format_exception(
            type(original), original, original.__traceback__))
        return f'<h2>Erro 500</h2><pre>{html.escape(texto)}</pre>', 500
    return 'Erro interno do servidor.', 500


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )