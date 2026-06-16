import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from graph.workflow import refund_graph
from models.schemas import ChatRequest, ChatResponse
from services.log_store import reasoning_logs

app = FastAPI(title="WorkPodd AI Refund Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    state = {
        "query": request.query,
        "order_id": "",
        "customer": {},
        "policy": "",
        "decision": {},
        "response": "",
        "logs": []
    }
    result = refund_graph.invoke(state)

    reasoning_logs.clear()
    reasoning_logs.extend(result["logs"])

    return {
        "response": result["response"],
        "logs": result["logs"]
    }


@app.get("/logs")
def get_logs():
    return {"logs": reasoning_logs}
