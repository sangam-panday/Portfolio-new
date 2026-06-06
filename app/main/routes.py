from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.ai_service import ask_ai

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/app')
def app_page():
    return render_template('app.html')

@main_bp.route('/ask', methods = ['GET', 'POST'])
@login_required
def ask():
    if request.method == 'GET':
        return render_template('ask.html')
    else:
        question = request.form.get('question')
        answer = ask_ai(question)
        return render_template('ask.html', question=question, answer=answer)