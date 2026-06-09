from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import (
    retrieve,
    generate_answer
)

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(data: QuestionRequest):

    chunks = retrieve(data.question)

    answer = generate_answer(
        data.question,
        chunks
    )

    return {
        "question": data.question,
        "answer": answer,
        "answer_chunks": chunks
    }