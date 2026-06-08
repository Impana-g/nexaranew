from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import retrieve

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(data: QuestionRequest):

    chunks = retrieve(data.question)

    return {
        "question": data.question,
        "answer_chunks": chunks
    }