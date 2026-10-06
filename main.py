import html
import os
import traceback
import uuid

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session
)
from werkzeug.utils import secure_filename

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import auth as firebase_auth
from google.api_core.exceptions import Conflict
from google.cloud.firestore_v1.base_query import FieldFilter


app = Flask(__name__)

# Em produção defina a variável de ambiente SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')


# ==========================================================
# FIREBASE (login, controle de 1 voto e banco de dados)
# ==========================================================

def obter_caminho_chave():
    """No Render a chave fica em /etc/secrets (Secret File).
    No computador local fica na mesma pasta do main.py."""
    caminho_render = '/etc/secrets/serviceAccountKey.json'
    if os.path.exists(caminho_render):
        return caminho_render
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'serviceAccountKey.json')


CAMINHO_CHAVE = obter_caminho_chave()

if not os.path.exists(CAMINHO_CHAVE):
    raise FileNotFoundError(
        'Chave do Firebase não encontrada. No computador, coloque o serviceAccountKey.json '
        'na pasta do projeto. No Render, adicione-o em Environment > Secret Files.'
    )

firebase_admin.initialize_app(credentials.Certificate(CAMINHO_CHAVE))
db = firestore.client()


def id_dispositivo_valido(valor):
    """Confere se o ID do aparelho tem formato de UUID."""
    try:
        uuid.UUID(valor)
        return True
    except (ValueError, TypeError):
        return False


def ja_votou_no_banco():
    """Confere no Firestore se a conta ou o aparelho da sessão já votou."""
    uid = session.get('uid')
    id_dispositivo = session.get('id_dispositivo')
    if uid and db.collection('votos').document(uid).get().exists:
        return True
    if id_dispositivo and db.collection('dispositivos').document(id_dispositivo).get().exists:
        return True
    return False


# ==========================================================
# CONFIGURAÇÃO DE UPLOAD
# ==========================================================

# Caminho absoluto: funciona mesmo se o main.py for executado de outra pasta
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Só aceita imagens e vídeos (evita que alguém envie arquivos perigosos para o site)
EXTENSOES_PERMITIDAS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.mp4', '.webm', '.mov',
}


def salvar_midias(arquivos):
    """Salva os arquivos enviados em static/uploads com um nome único.
    Devolve (lista_de_nomes_salvos, quantidade_ignorada)."""
    salvas = []
    ignoradas = 0

    for arquivo in arquivos:
        if not arquivo or not arquivo.filename:
            continue

        base, extensao = os.path.splitext(arquivo.filename)
        extensao = extensao.lower()

        if extensao not in EXTENSOES_PERMITIDAS:
            ignoradas += 1
            continue

        # O prefixo aleatório impede que um projeto sobrescreva a foto de outro
        # quando os dois enviam arquivos com o mesmo nome (ex.: "foto.jpg")
        base_segura = secure_filename(base) or 'midia'
        nome_final = f'{uuid.uuid4().hex[:8]}_{base_segura}{extensao}'

        arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_final))
        salvas.append(nome_final)

    return salvas, ignoradas


def apagar_arquivo_midia(nome_arquivo):
    """Remove um arquivo de static/uploads, se ele existir."""
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)


# ==========================================================
# ESTANDES NO FIRESTORE
# Coleção "estandes": um documento por projeto
# {turma, turma_busca, nome, resumo, midias, criadoEm}
# ==========================================================

def colecao_estandes():
    return db.collection('estandes')


def carregar_estandes():
    """Lista os estandes do banco, do mais novo para o mais antigo.
    Cada item vem com a chave 'id' (o ID do documento no Firestore)."""
    documentos = colecao_estandes().order_by(
        'criadoEm', direction=firestore.Query.DESCENDING
    ).stream()

    lista = []
    for doc in documentos:
        dados = doc.to_dict()
        dados['id'] = doc.id
        dados.setdefault('midias', [])
        dados.setdefault('resumo', '')
        lista.append(dados)
    return lista


def buscar_estande(estande_id):
    doc = colecao_estandes().document(estande_id).get()
    if not doc.exists:
        return None
    dados = doc.to_dict()
    dados['id'] = doc.id
    return dados


def turma_ja_cadastrada(turma, ignorar_id=None):
    """Confere se já existe estande com essa turma (sem diferenciar maiúsculas)."""
    consulta = colecao_estandes().where(
        filter=FieldFilter('turma_busca', '==', turma.lower())
    ).stream()
    return any(doc.id != ignorar_id for doc in consulta)


def estande_por_indice(index):
    """As rotas de edição usam a posição na lista (index).
    Carrega a lista do banco e devolve o estande dessa posição."""
    lista = carregar_estandes()
    if index < 0 or index >= len(lista):
        return None
    return lista[index]


# ==========================================================
# VOTAÇÃO: PERGUNTAS
# ==========================================================

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


def contar_votos():
    """Conta os votos direto do Firestore (coleção "votos").
    Cada documento é a cédula de uma pessoa: {'respostas': {'1': id, ..., '8': id}}.
    Devolve (contadores, votantes), onde contadores[i] = {id_do_estande: quantidade}."""
    total = len(PERGUNTAS_VOTACAO)
    contadores = [{} for _ in range(total)]
    votantes = 0

    for doc in db.collection('votos').stream():
        respostas = (doc.to_dict() or {}).get('respostas', {})
        votantes += 1
        for i in range(total):
            escolhido = respostas.get(str(i + 1))
            if escolhido:
                contadores[i][escolhido] = contadores[i].get(escolhido, 0) + 1

    return contadores, votantes


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

    if turma_ja_cadastrada(turma):
        flash(f'A turma "{turma}" já possui um estande cadastrado!', 'error')
        return redirect(url_for('pagina_descricao'))

    midias_salvas, ignoradas = salvar_midias(request.files.getlist('midias'))

    # Salva no Firestore (o ID do documento é o identificador usado na votação)
    estande_id = uuid.uuid4().hex
    try:
        colecao_estandes().document(estande_id).set({
            'turma': turma,
            'turma_busca': turma.lower(),
            'nome': (nome_projeto or 'Projeto sem título').strip(),
            'resumo': (resumo_projeto or '').strip(),
            'midias': midias_salvas,
            'criadoEm': firestore.SERVER_TIMESTAMP,
        })
    except Exception as erro:
        # Se o banco falhar, não deixa arquivos órfãos na pasta de uploads
        print('Erro ao salvar estande no Firestore:', erro)
        for arquivo in midias_salvas:
            apagar_arquivo_midia(arquivo)
        flash('Não foi possível salvar o estande agora. Tente novamente.', 'error')
        return redirect(url_for('pagina_descricao'))

    if ignoradas:
        flash(f'{ignoradas} arquivo(s) ignorado(s): envie apenas imagens ou vídeos.', 'error')

    flash('Estande cadastrado com sucesso!', 'success')
    return redirect(url_for('estandes'))


# ==========================================================
# LISTAGEM DOS ESTANDES
# ==========================================================

@app.route('/estandes')
def estandes():
    return render_template('estandes.html', estandes=carregar_estandes())


# ==========================================================
# LOGIN DO ESTUDANTE / REGISTRO
# ==========================================================

@app.route('/estandelogin')
def estudantelogin():
    return render_template('login/estudantelogin.html')


@app.route('/register')
def register():
    return render_template('login/register.html')


# ----------------------------------------------------------
# LOGIN COM GOOGLE (recebe o token enviado pelo firebase.js)
# ----------------------------------------------------------

@app.route('/login/google', methods=['POST'])
def login_google():
    id_token = request.form.get('id_token', '')
    id_dispositivo = request.form.get('id_dispositivo', '')

    if not id_token or not id_dispositivo_valido(id_dispositivo):
        flash('Não foi possível confirmar o login. Tente novamente.', 'error')
        return redirect(url_for('register'))

    # Confere se o token é verdadeiro (assinado pelo Firebase e não expirado)
    try:
        dados = firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
    except Exception as erro:
        print('Token inválido:', erro)
        flash('Não foi possível confirmar o login. Tente novamente.', 'error')
        return redirect(url_for('register'))

    uid = dados['uid']

    # Começa uma sessão limpa para esta pessoa
    session.clear()
    session['uid'] = uid
    session['email'] = dados.get('email', '')
    session['nome'] = dados.get('name', session['email'])
    session['id_dispositivo'] = id_dispositivo

    # Esta conta ou este aparelho já votou?
    aparelho_votou = db.collection('dispositivos').document(id_dispositivo).get().exists
    conta_votou = db.collection('votos').document(uid).get().exists
    session['votou'] = aparelho_votou or conta_votou

    if session['votou']:
        flash('Você já votou com esta conta ou neste aparelho. Obrigado pela participação!', 'error')
        return redirect(url_for('index'))

    return redirect(url_for('iniciar_votacao'))


@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('register'))


# ==========================================================
# GERENCIAMENTO DE PROJETOS
# ==========================================================

@app.route('/projetos')
def listar_projetos():
    return render_template('projetos/listar.html', estandes=carregar_estandes())


# ----------------------------------------------------------
# EDITAR PROJETO
# ----------------------------------------------------------

@app.route('/projetos/editar/<int:index>', methods=['GET', 'POST'])
def editar_projeto(index):

    estande = estande_por_indice(index)
    if estande is None:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

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

        if turma_ja_cadastrada(turma, ignorar_id=estande['id']):
            flash(f'A turma "{turma}" já possui outro projeto cadastrado!', 'error')
            return redirect(url_for('editar_projeto', index=index))

        colecao_estandes().document(estande['id']).update({
            'nome': nome.strip(),
            'turma': turma,
            'turma_busca': turma.lower(),
            'resumo': resumo.strip() if resumo else '',
        })

        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_projetos'))

    return render_template('projetos/editar.html', estande=estande, index=index)


# ----------------------------------------------------------
# EDITAR MÍDIAS
# ----------------------------------------------------------

@app.route('/projetos/editar-midias/<int:index>', methods=['GET', 'POST'])
def editar_midias(index):

    estande = estande_por_indice(index)
    if estande is None:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    if request.method == 'POST':
        novas, ignoradas = salvar_midias(request.files.getlist('midias'))

        if novas:
            # ArrayUnion acrescenta na lista do banco sem sobrescrever o que já existe
            colecao_estandes().document(estande['id']).update({
                'midias': firestore.ArrayUnion(novas),
            })

        if ignoradas:
            flash(f'{ignoradas} arquivo(s) ignorado(s): envie apenas imagens ou vídeos.', 'error')

        flash('Mídias atualizadas com sucesso!', 'success')
        return redirect(url_for('editar_midias', index=index))

    return render_template('projetos/editar_midias.html', estande=estande, index=index)


# ----------------------------------------------------------
# EXCLUIR PROJETO
# ----------------------------------------------------------

@app.route('/projetos/excluir/<int:index>', methods=['POST'])
def excluir_projeto(index):

    estande = estande_por_indice(index)
    if estande is None:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    colecao_estandes().document(estande['id']).delete()

    # Os votos que já apontavam para este projeto continuam no banco,
    # mas o ranking só conta projetos que ainda existem, então eles são ignorados.

    for arquivo in estande.get('midias', []):
        apagar_arquivo_midia(arquivo)

    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('listar_projetos'))


# ----------------------------------------------------------
# EXCLUIR UMA MÍDIA
# ----------------------------------------------------------

@app.route('/projetos/excluir-midia/<int:index>/<int:midia_index>', methods=['POST'])
def excluir_midia(index, midia_index):

    estande = estande_por_indice(index)
    if estande is None:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('listar_projetos'))

    midias = list(estande['midias'])

    if midia_index < 0 or midia_index >= len(midias):
        flash('Mídia não encontrada!', 'error')
        return redirect(url_for('editar_midias', index=index))

    arquivo = midias[midia_index]

    # ArrayRemove tira só este arquivo da lista no banco
    colecao_estandes().document(estande['id']).update({
        'midias': firestore.ArrayRemove([arquivo]),
    })
    apagar_arquivo_midia(arquivo)

    flash('Mídia excluída com sucesso!', 'success')
    return redirect(url_for('editar_midias', index=index))


# ==========================================================
# VOTAÇÃO  (uma cédula com 8 perguntas, 1 projeto por pergunta)
# ==========================================================

def primeira_sem_resposta(respostas):
    for i in range(1, len(PERGUNTAS_VOTACAO) + 1):
        if str(i) not in respostas:
            return i
    return len(PERGUNTAS_VOTACAO)


@app.route('/votacao')
def iniciar_votacao():
    """Leva sempre para as perguntas, mesmo sem projetos cadastrados.
    Só não deixa entrar quem não fez login ou quem já votou."""
    if 'uid' not in session or 'id_dispositivo' not in session:
        return redirect(url_for('register'))

    if ja_votou_no_banco():
        session['votou'] = True

    if session.get('votou'):
        flash('Você já votou com esta conta ou neste aparelho. Obrigado pela participação!', 'error')
        return redirect(url_for('index'))

    return redirect(url_for(
        'exibir_pergunta',
        numero=primeira_sem_resposta(session.get('respostas', {}))
    ))


@app.route('/votacao/pergunta/<int:numero>', methods=['GET', 'POST'])
def exibir_pergunta(numero):
    """Uma pergunta por tela. A resposta de cada tela fica na sessão
    e a cédula só é gravada no banco ao finalizar a pergunta 8.
    Sem projetos cadastrados, a tela abre normalmente, mas não aceita envio."""
    if 'uid' not in session or 'id_dispositivo' not in session:
        return redirect(url_for('register'))

    if ja_votou_no_banco():
        session['votou'] = True

    if session.get('votou'):
        flash('Você já votou com esta conta ou neste aparelho. Obrigado pela participação!', 'error')
        return redirect(url_for('index'))

    lista = carregar_estandes()
    total = len(PERGUNTAS_VOTACAO)

    if numero < 1 or numero > total:
        return redirect(url_for('exibir_pergunta', numero=1))

    ids_validos = {e['id'] for e in lista}
    respostas = {
        k: v for k, v in session.get('respostas', {}).items()
        if v in ids_validos
    }

    if request.method == 'POST':
        if not lista:
            flash('Ainda não há projetos cadastrados para votação.', 'error')
            return redirect(url_for('exibir_pergunta', numero=numero))

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

        # Registra no Firestore: 1 voto por conta e 1 por aparelho.
        # O "create" falha se o documento já existir, e isso bloqueia o voto repetido.
        # A cédula salva em "votos" é o que o ranking usa para contar.
        try:
            batch = db.batch()
            batch.create(db.collection('votos').document(session['uid']), {
                'email': session.get('email'),
                'dispositivo': session['id_dispositivo'],
                'respostas': respostas,
                'criadoEm': firestore.SERVER_TIMESTAMP,
            })
            batch.create(db.collection('dispositivos').document(session['id_dispositivo']), {
                'uid': session['uid'],
                'criadoEm': firestore.SERVER_TIMESTAMP,
            })
            batch.commit()
        except Conflict:
            session['votou'] = True
            session.pop('respostas', None)
            flash('Esta conta ou este aparelho já registrou um voto.', 'error')
            return redirect(url_for('index'))
        except Exception as erro:
            print('Erro ao registrar voto no Firestore:', erro)
            flash('Não foi possível registrar o voto agora. Tente novamente.', 'error')
            return redirect(url_for('exibir_pergunta', numero=total))

        session['votou'] = True
        session.pop('respostas', None)

        flash('Voto registrado com sucesso! Obrigado pela participação.', 'success')
        return redirect(url_for('ranking'))

    # GET: não deixa pular perguntas
    faltando = primeira_sem_resposta(respostas)
    if numero > faltando:
        return redirect(url_for('exibir_pergunta', numero=faltando))

    return render_template(
        'votacao/etapa.html',
        numero=numero,
        total=total,
        pergunta=PERGUNTAS_VOTACAO[numero - 1],
        estandes=lista,
        escolhida=respostas.get(str(numero)),
    )


@app.route('/ranking')
def ranking():
    """Vencedor de cada pergunta + classificação geral (soma dos votos).
    Os votos são lidos do Firestore, então o ranking não zera ao reiniciar o servidor."""
    lista = carregar_estandes()
    votos, votantes = contar_votos()

    categorias = []
    total_geral = {e['id']: 0 for e in lista}

    for i, item in enumerate(PERGUNTAS_VOTACAO):
        linhas = []
        for e in lista:
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
        ({'estande': e, 'qtd': total_geral[e['id']]} for e in lista),
        key=lambda l: l['qtd'], reverse=True,
    )

    return render_template(
        'votacao/ranking.html',
        categorias=categorias,
        geral=geral,
        votantes=votantes,
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