from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ai_engine import ask_question

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "AI Data Analyst API is running"
    }


@app.get("/chart")
def get_chart():

    return FileResponse("chart.png", media_type="image/png")


class QuestionRequest(BaseModel):

    question: str


@app.post("/ask")
def ask(request: QuestionRequest):

    answer = ask_question(request.question)

    if isinstance(answer, dict):

        return {
            "question": request.question,
            "answer": answer["answer"],
            "result": answer["result"],
            "chart_type": answer["chart_type"],
            "chart_path": answer["chart_path"]
        }

    return {
        "question": request.question,
        "answer": answer,
        "result": [],
        "chart_type": "NONE",
        "chart_path": None
    }