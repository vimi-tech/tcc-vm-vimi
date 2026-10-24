from flask import Blueprint, render_template, request, flash, redirect, url_for

from flask import Blueprint, render_template

project_bp = Blueprint('project', __name__)


@project_bp.route('/project', methods=['GET', 'POST'])
def project():
    return render_template('project/project.html')