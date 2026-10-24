from flask import Blueprint, render_template

# O nome da variável precisa ser o mesmo usado no @...route e no main.py
project_bp = Blueprint('project', __name__)


@project_bp.route('/project', methods=['GET', 'POST'])
def project():
    return render_template('project/project.html')