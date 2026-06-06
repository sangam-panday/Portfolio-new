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


def ask_ai(question: str) -> str:
    answer = chain.invoke({"question": question})
    return answer