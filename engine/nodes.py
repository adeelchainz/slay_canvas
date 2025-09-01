from typing import Any, Dict
from engine.langraph_engine import engine as lg_engine


class Node:
    def __init__(self, name: str):
        self.name = name

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class TranscriptionNode(Node):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        audio_bytes = inputs.get('audio')
        return await lg_engine.transcribe(audio_bytes)


class ImageAnalysisNode(Node):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        image_bytes = inputs.get('image')
        return await lg_engine.analyze_image(image_bytes)


class LLMNode(Node):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs.get('prompt')
        return await lg_engine.chat(prompt)
