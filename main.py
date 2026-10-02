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

# Votos por estande: {id_do_estande: [[8 notas], [8 notas], ...]}
votos = {}

# As 8 perguntas oficiais da votação (nota de 1 a 5 em cada uma)
PERGUNTAS_VOTACAO = [
    "Como você avalia a inovação e criatividade do projeto?",
    "O protótipo/demonstração prática funcionou corretamente?",
    "A equipe apresentou o projeto com clareza e domínio do assunto?",
    "O projeto resolve um problema real da comunidade/mercado?",
    "Qual o nível de acabamento e organização visual do estande?",
    "A documentação/material de apoio estava bem estruturada?",
    "O projeto utilizou tecnologias adequadas ao proposto?",
    "Qual sua nota geral para a experiência no estande?",
]


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
    votos.pop(estande['id'], None)

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
# VOTAÇÃO
# ==========================================================

@app.route('/votacao')
def iniciar_votacao():
    """Lista os projetos. Se não houver nenhum, a página mostra
    'Nenhum projeto disponível para votação'."""
    for e in estandes_cadastrados:
        e.setdefault('id', uuid.uuid4().hex)
        e.setdefault('resumo', '')
        e['resumo'] = e['resumo'] or ''

    return render_template(
        'votacao/lista.html',
        estandes=estandes_cadastrados,
        ja_votou=session.get('votou_em', []),
        total_perguntas=len(PERGUNTAS_VOTACAO),
    )


@app.route('/votacao/<estande_id>', methods=['GET', 'POST'])
def votar_estande(estande_id):
    """Mostra as 8 perguntas de UM projeto e salva as notas."""

    estande = buscar_estande(estande_id)
    if not estande:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('iniciar_votacao'))

    ja_votou = session.get('votou_em', [])
    if estande_id in ja_votou:
        flash('Você já avaliou este projeto.', 'error')
        return redirect(url_for('iniciar_votacao'))

    if request.method == 'POST':
        notas = []
        for i in range(len(PERGUNTAS_VOTACAO)):
            try:
                nota = int(request.form.get(f'nota_{i + 1}', ''))
            except ValueError:
                nota = 0
            if nota < 1 or nota > 5:
                flash('Responda todas as perguntas com uma nota de 1 a 5.', 'error')
                return redirect(url_for('votar_estande', estande_id=estande_id))
            notas.append(nota)

        votos.setdefault(estande_id, []).append(notas)
        session['votou_em'] = ja_votou + [estande_id]

        flash(f'Voto registrado para "{estande["nome"]}". Obrigado!', 'success')
        return redirect(url_for('iniciar_votacao'))

    return render_template(
        'votacao/avaliar.html',
        estande=estande,
        perguntas=PERGUNTAS_VOTACAO,
    )


@app.route('/ranking')
def ranking():
    """Média das notas de cada projeto, do melhor para o pior."""
    lista = []
    for estande in estandes_cadastrados:
        votos_estande = votos.get(estande['id'], [])
        qtd = len(votos_estande)
        if qtd:
            medias = [
                sum(v[i] for v in votos_estande) / qtd
                for i in range(len(PERGUNTAS_VOTACAO))
            ]
            geral = sum(medias) / len(medias)
        else:
            geral = 0
        lista.append({'estande': estande, 'qtd_votos': qtd, 'media': round(geral, 2)})

    lista.sort(key=lambda r: (r['media'], r['qtd_votos']), reverse=True)
    return render_template('votacao/ranking.html', ranking=lista)


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