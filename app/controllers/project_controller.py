from flask import Blueprint, render_template, request, flash, redirect, url_for

city_bp = Blueprint('project', __name__)

@city_bp.route('/project', methods=['GET', 'POST'])
def city():
    return render_template('project/project.html')