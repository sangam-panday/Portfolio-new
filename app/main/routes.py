from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import ChatHistory
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
    previous_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.asc()).all()
    
    if request.method == 'GET':
        return render_template('ask.html', previous_chats=previous_chats)
    else:
        question = request.form.get('question')
        answer = ask_ai(question, current_user.id)
        # Fetch updated chat history after saving
        previous_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.asc()).all()
        return render_template('ask.html', previous_chats=previous_chats, question=question, answer=answer)