import html
import os
import re
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

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:          # biblioteca ainda não instalada: usa a pasta local
    cloudinary = None


app = Flask(__name__)

# Em produção defina a variável de ambiente SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')


# ==========================================================
# FIREBASE (login, controle de 1 voto e banco de dados)
# ==========================================================

from app.config.firebase import init_firebase, get_firestore_client, FIREBASE_PROJECT_ID

try:
    init_firebase()
    db = get_firestore_client()
except Exception as erro_fb:
    print(f"Aviso ao inicializar Firebase ({FIREBASE_PROJECT_ID}): {erro_fb}")
    db = None



def id_dispositivo_valido(valor):
    """Confere se o ID do aparelho tem formato de UUID."""
    try:
        uuid.UUID(valor)
        return True
    except (ValueError, TypeError):
        return False


def ja_votou_no_banco():
    """Confere no Firestore se a conta ou o aparelho da sessão já votou."""
    global db
    if db is None:
        db = get_firestore_client()
    if db is None:
        return False
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


# ----------------------------------------------------------
# ARMAZENAMENTO DAS MÍDIAS
# Com as variáveis CLOUDINARY_* definidas no Render, as fotos e vídeos vão
# para o Cloudinary (ficam guardados para sempre e o Firestore guarda o link).
# Sem elas, o site continua salvando em static/uploads (que o Render apaga
# a cada reinício/deploy).
# ----------------------------------------------------------

PASTA_SEGREDOS = '/etc/secrets'


def ler_segredo(nome):
    """Lê um valor secreto: primeiro como variável de ambiente (Environment
    Variables do Render) e, se não existir, como Secret File em /etc/secrets."""
    valor = os.environ.get(nome)
    if valor and valor.strip():
        return valor.strip()
    caminho = os.path.join(PASTA_SEGREDOS, nome)
    if os.path.isfile(caminho):
        with open(caminho, encoding='utf-8') as arquivo:
            return arquivo.read().strip() or None
    return None


_CLOUD_NAME = ler_segredo('CLOUDINARY_CLOUD_NAME')
_API_KEY = ler_segredo('CLOUDINARY_API_KEY')
_API_SECRET = ler_segredo('CLOUDINARY_API_SECRET')

CLOUDINARY_ATIVO = bool(cloudinary and _CLOUD_NAME and _API_KEY and _API_SECRET)

if CLOUDINARY_ATIVO:
    cloudinary.config(
        cloud_name=_CLOUD_NAME,
        api_key=_API_KEY,
        api_secret=_API_SECRET,
        secure=True,
    )

# Aparece nos Logs do Render quando o site inicia
print('Cloudinary ativo:', CLOUDINARY_ATIVO,
      '| biblioteca instalada:', cloudinary is not None,
      '| variáveis definidas:', bool(_CLOUD_NAME and _API_KEY and _API_SECRET))


def eh_url(nome):
    return str(nome).startswith(('http://', 'https://'))


@app.template_global()
def url_midia(nome):
    """Endereço da mídia: link do Cloudinary ou arquivo em static/uploads."""
    if eh_url(nome):
        return nome
    return url_for('static', filename='uploads/' + nome)


@app.template_global()
def eh_video(nome):
    return str(nome).lower().split('?')[0].endswith(('.mp4', '.webm', '.mov'))


def salvar_midias(arquivos):
    """Envia os arquivos (Cloudinary ou static/uploads) com um nome único.
    Devolve (lista_de_nomes_ou_links_salvos, quantidade_nao_enviada)."""
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
        sufixo = f'{uuid.uuid4().hex[:8]}_{base_segura}'

        if CLOUDINARY_ATIVO:
            try:
                arquivo.stream.seek(0)
                resultado = cloudinary.uploader.upload(
                    arquivo.stream,
                    resource_type='auto',
                    folder='feirascore',
                    public_id=sufixo,
                )
                salvas.append(resultado['secure_url'])
            except Exception as erro:
                print('Erro ao enviar para o Cloudinary:', erro)
                ignoradas += 1
        else:
            nome_final = f'{sufixo}{extensao}'
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_final))
            salvas.append(nome_final)

    return salvas, ignoradas


def apagar_arquivo_midia(nome_arquivo):
    """Apaga a mídia: no Cloudinary (se for um link de lá) ou em static/uploads."""
    if eh_url(nome_arquivo):
        if CLOUDINARY_ATIVO and 'res.cloudinary.com' in nome_arquivo and '/upload/' in nome_arquivo:
            try:
                tipo = 'video' if '/video/upload/' in nome_arquivo else 'image'
                partes = nome_arquivo.split('/upload/', 1)[1].split('/')
                if partes and re.fullmatch(r'v\d+', partes[0]):
                    partes = partes[1:]
                public_id = os.path.splitext('/'.join(partes))[0]
                cloudinary.uploader.destroy(public_id, resource_type=tipo)
            except Exception as erro:
                print('Erro ao apagar mídia no Cloudinary:', erro)
        return

    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)


def colecao_estandes():
    global db
    if db is None:
        db = get_firestore_client()
    if db is None:
        raise ConnectionError("Cliente do Firestore não conectado ao projeto 'tccfeirascore'.")
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

    global db
    if db is None:
        db = get_firestore_client()
    if db is None:
        return contadores, votantes

    for doc in db.collection('votos').stream():
        respostas = (doc.to_dict() or {}).get('respostas', {})
        votantes += 1
        for i in range(total):
            escolhido = respostas.get(str(i + 1))
            if escolhido:
                contadores[i][escolhido] = contadores[i].get(escolhido, 0) + 1

    return contadores, votantes


# ==========================================================
# BLUEPRINT DE AUTENTICAÇÃO E PROJETOS
# ==========================================================

try:
    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)
except Exception as e:
    print("Aviso: não foi possível carregar o auth_controller:", e)

try:
    from app.services.project_service import ProjectService
    project_service = ProjectService()
except Exception as e:
    project_service = None
    print("Aviso: não foi possível inicializar o ProjectService:", e)


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route("/")
def index():
    return render_template('index.html', site='Feirascore')


# ==========================================================
# CADASTRO DE ESTANDE / PROJETO (VINCULADO A TURMA)
# ==========================================================

@app.route('/descricaoprojeto', methods=['GET', 'POST'])
def pagina_descricao():
    if request.method == 'POST':
        return processar_envio_estande()
    turma = request.args.get('turma', '')
    return render_template('pages/descricaoprojeto.html', turma=turma)


@app.route('/cadastrar-estande', methods=['POST'])
def cadastrar_estande():
    return processar_envio_estande()


def processar_envio_estande():
    turma = request.form.get('turma')
    nome_projeto = request.form.get('nome') or request.form.get('nome_projeto')
    resumo_projeto = request.form.get('resumo') or request.form.get('resumo_projeto')
    arquivos = request.files.getlist('midias')

    if project_service:
        try:
            saved_project, ignoradas = project_service.register_project(
                turma=turma,
                nome=nome_projeto,
                resumo=resumo_projeto,
                arquivos_midia=arquivos
            )
            if ignoradas:
                flash(f'{ignoradas} arquivo(s) não enviado(s): use imagens ou vídeos e confira o tamanho.', 'warning')
            flash(f'Projeto "{saved_project.nome}" da turma "{saved_project.turma}" cadastrado com sucesso!', 'success')
            return redirect(url_for('estandes'))
        except ValueError as ve:
            flash(str(ve), 'error')
            return redirect(url_for('pagina_descricao', turma=turma))
        except Exception as erro:
            print('Erro ao cadastrar projeto via ProjectService:', erro)
            flash(f'Não foi possível salvar o projeto agora: {erro}', 'error')
            return redirect(url_for('pagina_descricao', turma=turma))

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
        return redirect(url_for('pagina_descricao', turma=turma))

    if ignoradas:
        flash(f'{ignoradas} arquivo(s) não enviado(s): use imagens ou vídeos e confira o tamanho.', 'error')

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
    global db
    if db is None:
        db = get_firestore_client()
    aparelho_votou = db.collection('dispositivos').document(id_dispositivo).get().exists if db else False
    conta_votou = db.collection('votos').document(uid).get().exists if db else False
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
            flash(f'{ignoradas} arquivo(s) não enviado(s): use imagens ou vídeos e confira o tamanho.', 'error')

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
            global db
            if db is None:
                db = get_firestore_client()
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
