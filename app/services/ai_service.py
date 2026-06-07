from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser,StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from pydantic import BaseModel, Field
from typing import Literal
import os
from flask import request, jsonify
from dotenv import load_dotenv
load_dotenv()

from app.models import ChatHistory
from app.extension import db

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not hf_token:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment variables")

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="conversational",
    max_new_tokens=100,
    temperature=0.1,
    huggingfacehub_api_token=hf_token
)

chat_model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate(
    template="""You are a helpful and friendly AI assistant. Use the conversation history below to provide context-aware answers.

Conversation History:
{history}

User Question: {question}

Provide a helpful answer based on the conversation history and the new question.
dont gimme too many text, keep it short and to the point.
answer on the most recent question asked by the user, and dont answer on the old questions, just use them as a context for the most recent question.""",
    input_variables=["history", "question"]
)

parser = StrOutputParser()

chain = prompt | chat_model | parser


def ask_ai(question: str, user_id: int) -> str:
    # Fetch previous conversations
    previous_chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.asc()).limit(10).all()
    
    # Build conversation history context
    history_text = ""
    for chat in previous_chats:
        history_text += f"User: {chat.question}\nAssistant: {chat.answer}\n\n"
    
    if not history_text:
        history_text = "No previous conversations."
    
    # Generate answer with context
    answer = chain.invoke({"history": history_text, "question": question})

    # Save to database
    chat_history = ChatHistory(
        user_id=user_id,
        question=question,
        answer=answer
    )
    db.session.add(chat_history)
    db.session.commit()

    return answer

