from engine.orchestrator import orchestrator
from engine.langraph_engine import engine as langraph_engine


class EngineAdapter:
    def __init__(self):
        self.orch = orchestrator
        self.langraph = langraph_engine

    async def transcribe(self, audio_bytes: bytes):
        # prefer orchestrator (which uses nodes -> langraph under the hood)
        return await self.orch.transcribe_audio(audio_bytes)

    async def analyze_image(self, image_bytes: bytes):
        return await self.orch.analyze_image(image_bytes)

    async def chat(self, prompt: str, context: dict | None = None):
        return await self.orch.chat(prompt, context)


engine = EngineAdapter()
