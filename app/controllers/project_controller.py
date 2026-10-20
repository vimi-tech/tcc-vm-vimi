from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.services.project_service import ProjectService

project_bp = Blueprint('project', __name__)
project_service = ProjectService()


@project_bp.route('/descricaoprojeto', methods=['GET', 'POST'])
def pagina_descricao():
    """Rota para exibição e processamento do formulário de cadastro de Projeto vinculado à Turma."""
    if request.method == 'POST':
        turma = request.form.get('turma')
        nome_projeto = request.form.get('nome') or request.form.get('nome_projeto')
        resumo = request.form.get('resumo') or request.form.get('resumo_projeto')
        arquivos = request.files.getlist('midias')

        try:
            saved_project, ignoradas = project_service.register_project(
                turma=turma,
                nome=nome_projeto,
                resumo=resumo,
                arquivos_midia=arquivos
            )

            if ignoradas > 0:
                flash(f'{ignoradas} arquivo(s) não enviado(s): use imagens ou vídeos no formato correto.', 'warning')

            flash(f'Projeto "{saved_project.nome}" da turma "{saved_project.turma}" cadastrado com sucesso!', 'success')
            return redirect(url_for('estandes'))

        except ValueError as ve:
            flash(str(ve), 'error')
            return redirect(url_for('project.pagina_descricao', turma=turma))
        except Exception as e:
            flash(f'Não foi possível salvar o projeto agora: {str(e)}', 'error')
            return redirect(url_for('project.pagina_descricao', turma=turma))

    turma_param = request.args.get('turma', '')
    return render_template('pages/descricaoprojeto.html', turma=turma_param)


@project_bp.route('/projetos')
def listar_projetos():
    """Lista todos os projetos cadastrados a partir do Firestore."""
    projetos = project_service.get_all_projects()
    # Converte para dicionários para compatibilidade com os templates
    projetos_dict = [p.to_dict() | {'id': p.id} for p in projetos]
    return render_template('projetos.html', estandes=projetos_dict, projetos=projetos)


@project_bp.route('/projetos/editar/<string:project_id>', methods=['GET', 'POST'])
def editar_projeto(project_id):
    """Edita as informações do projeto e da turma."""
    projeto = project_service.get_project_by_id(project_id)
    if not projeto:
        flash('Projeto não encontrado!', 'error')
        return redirect(url_for('project.listar_projetos'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        turma = request.form.get('turma')
        resumo = request.form.get('resumo')

        if not nome or not turma:
            flash('Nome e turma são obrigatórios!', 'error')
            return redirect(url_for('project.editar_projeto', project_id=project_id))

        try:
            project_service.update_project(project_id, {
                'nome': nome.strip(),
                'turma': turma.strip(),
                'resumo': (resumo or '').strip()
            })
            flash('Projeto atualizado com sucesso!', 'success')
            return redirect(url_for('project.listar_projetos'))
        except ValueError as ve:
            flash(str(ve), 'error')
            return redirect(url_for('project.editar_projeto', project_id=project_id))

    return render_template('projetos/editar.html', projeto=projeto)