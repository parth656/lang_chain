from langgraph.graph import START, END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import *
from common import Rag
import json


class InformationState(TypedDict):
    content: str
    raiseTicket: str
    question: str


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def create_model():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", temperature=0, api_key=api_key
    )
    return model


def ask_rag(state: InformationState):
    rg = Rag()
    context = rg.retrieval(state["question"])
    "This will used to retrieve content"
    user_prompt = f"""
    You are a helpful support assistant. Answer the user's question using ONLY the information in the context below.

    Rules:
    - Base your answer strictly on the context. Do not use outside knowledge or make assumptions.
    - If the context does not contain the answer, say so briefly instead of guessing.
    - Keep the answer clear and concise.

    Ticket logic:
    - Set "raiseTicket" to "required" ONLY if the user's intent is to raise/create a support ticket, report an unresolved issue, or request human help.
    - Otherwise set it to "not_required".

    Context:
    {context}

    Question:
    {state["question"]}

    Return ONLY valid JSON in this exact format (no extra text):
    {{
    "content": "your answer here",
    "raiseTicket": "required" or "not_required"
    }}
    """
    model = create_model()
    res = model.invoke(user_prompt)
    data = json.loads(res.content[0]["text"])
    return {"content": data["content"], "raiseTicket": data["raiseTicket"]}


def build_graph():
    builder = StateGraph(InformationState)
    builder.add_node("ask_rag", ask_rag)
    builder.add_edge(START, "ask_rag")
    builder.add_edge("ask_rag", END)
    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    question = input("Enter any question: ")
    response = graph.invoke({"content": "", "raiseTicket": "", "question": question})
    print(response)
