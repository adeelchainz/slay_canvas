from fastapi import APIRouter, UploadFile, File, Depends
from app.schemas.ai import ChatRequest, ChatResponse
from app.utils.auth import get_current_user_id
from engine.adapter import engine
from app.services import ai_service

router = APIRouter()


@router.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest, user_id: int = Depends(get_current_user_id)):
    # For now, concatenate messages into a prompt
    prompt = '\n'.join([f"{m.role}: {m.content}" for m in req.messages])
    res = await engine.chat(prompt)
    return ChatResponse(reply=res.get('text', ''), sources=res.get('sources'))


@router.post('/transcribe', response_model=ChatResponse)
async def transcribe(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    audio = await file.read()
    res = await engine.transcribe(audio)
    return ChatResponse(reply=res.get('transcript', ''))


@router.post('/analyze_image', response_model=ChatResponse)
async def analyze_image(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    img = await file.read()
    res = await engine.analyze_image(img)
    return ChatResponse(reply=res.get('description', ''))


@router.post('/summarize', response_model=ChatResponse)
async def summarize(body: dict, user_id: int = Depends(get_current_user_id)):
    text = body.get('text', '')
    res = await ai_service.summarize_text(text)
    return ChatResponse(reply=res)


@router.post('/qa', response_model=ChatResponse)
async def qa(body: dict, user_id: int = Depends(get_current_user_id)):
    context = body.get('context', '')
    question = body.get('question', '')
    res = await ai_service.answer_question(context, question)
    return ChatResponse(reply=res)


@router.post('/generate', response_model=ChatResponse)
async def generate(body: dict, user_id: int = Depends(get_current_user_id)):
    prompt = body.get('prompt', '')
    res = await ai_service.generate_from_prompt(prompt)
    return ChatResponse(reply=res)
