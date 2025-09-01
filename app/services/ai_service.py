from engine.adapter import engine


async def summarize_text(text: str) -> str:
    # Use engine to summarize (Langraph LLM node)
    res = await engine.chat(f"Summarize this:\n\n{text}")
    return res.get('text', '')


async def generate_from_prompt(prompt: str) -> str:
    res = await engine.chat(prompt)
    return res.get('text', '')


async def answer_question(context: str, question: str) -> str:
    res = await engine.chat(f"Context:\n{context}\n\nQuestion: {question}\nAnswer:")
    return res.get('text', '')
