from flask import Blueprint, render_template, request
from flask_login import login_required
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser,StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from pydantic import BaseModel, Field
from typing import Literal
import os
from flask import request, jsonify

api_token = os.getenv("HUGGINGFACE_API_KEY")

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="conversational",
    max_new_tokens=100,
    temperature=0.1,
    huggingfacehub_api_token=api_token,
)

chat_model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate(
    template="You are a helpful assistant. Answer the following question: {question}",
    input_variables=["question"]
)

parser = StrOutputParser()

chain = prompt | chat_model | parser

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
        answer = chain.invoke({"question": question})
        return render_template('ask.html', question=question, answer=answer)