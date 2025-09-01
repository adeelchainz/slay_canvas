from typing import Any, Dict
from engine.nodes import TranscriptionNode, ImageAnalysisNode, LLMNode


class Orchestrator:
    def __init__(self):
        self.nodes = {
            'transcribe': TranscriptionNode('transcribe'),
            'image_analyze': ImageAnalysisNode('image_analyze'),
            'llm': LLMNode('llm'),
        }

    async def transcribe_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        return await self.nodes['transcribe'].run({'audio': audio_bytes})

    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        return await self.nodes['image_analyze'].run({'image': image_bytes})

    async def chat(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = {'prompt': prompt}
        if context:
            payload.update(context)
        return await self.nodes['llm'].run(payload)


orchestrator = Orchestrator()
