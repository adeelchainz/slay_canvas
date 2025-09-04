"""
AI Agents for Slay Canvas using LangGraph
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
from pydantic import BaseModel

from app.core.config import settings


class AgentState(BaseModel):
    """Shared state between agents"""
    media_file_id: int
    file_path: str
    file_type: str
    metadata: Dict[str, Any] = {}
    transcription: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = []
    insights: Dict[str, Any] = {}
    content_generated: Dict[str, str] = {}
    errors: List[str] = []
    processing_status: str = "pending"


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm_openai = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4",
            temperature=0.1
        ) if settings.OPENAI_API_KEY else None
        
        self.llm_anthropic = ChatAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            model="claude-3-sonnet-20240229",
            temperature=0.1
        ) if settings.ANTHROPIC_API_KEY else None
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state"""
        pass
    
    def get_llm(self, provider: str = "openai"):
        """Get LLM instance by provider"""
        if provider == "openai" and self.llm_openai:
            return self.llm_openai
        elif provider == "anthropic" and self.llm_anthropic:
            return self.llm_anthropic
        else:
            raise ValueError(f"LLM provider {provider} not available or configured")


class TranscriptionAgent(BaseAgent):
    """Agent responsible for transcribing audio/video content"""
    
    def __init__(self):
        super().__init__("TranscriptionAgent")
    
    async def process(self, state: AgentState) -> AgentState:
        """Transcribe audio/video files"""
        try:
            if state.file_type not in ["audio", "video"]:
                state.processing_status = "skipped"
                return state
            
            # For now, we'll simulate transcription
            # In production, integrate with OpenAI Whisper or similar
            state.transcription = await self._transcribe_file(state.file_path)
            state.processing_status = "transcribed"
            
            return state
            
        except Exception as e:
            state.errors.append(f"Transcription error: {str(e)}")
            state.processing_status = "error"
            return state
    
    async def _transcribe_file(self, file_path: str) -> str:
        """Simulate file transcription (replace with actual Whisper integration)"""
        # This is a placeholder - integrate with OpenAI Whisper API
        await asyncio.sleep(1)  # Simulate processing time
        return f"Transcription of {file_path} - This is a simulated transcription."


class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing content and extracting insights"""
    
    def __init__(self):
        super().__init__("AnalysisAgent")
    
    async def process(self, state: AgentState) -> AgentState:
        """Analyze content and extract insights"""
        try:
            content = state.transcription or "No transcription available"
            
            # Generate summary
            state.summary = await self._generate_summary(content)
            
            # Extract tags
            state.tags = await self._extract_tags(content)
            
            # Generate insights
            state.insights = await self._generate_insights(content, state.file_type)
            
            state.processing_status = "analyzed"
            return state
            
        except Exception as e:
            state.errors.append(f"Analysis error: {str(e)}")
            state.processing_status = "error"
            return state
    
    async def _generate_summary(self, content: str) -> str:
        """Generate content summary using LLM"""
        try:
            llm = self.get_llm("openai")
            
            prompt = f"""
            Please provide a concise summary of the following content in 2-3 sentences:
            
            Content: {content[:2000]}...
            
            Summary:
            """
            
            response = await llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception:
            return f"Summary: Content analysis of {len(content)} characters."
    
    async def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        try:
            llm = self.get_llm("openai")
            
            prompt = f"""
            Extract 5-7 relevant tags from the following content. Return only the tags separated by commas:
            
            Content: {content[:1500]}...
            
            Tags:
            """
            
            response = await llm.ainvoke(prompt)
            tags = [tag.strip() for tag in response.content.split(",")]
            return tags[:7]  # Limit to 7 tags
            
        except Exception:
            return ["media", "content", "analysis"]
    
    async def _generate_insights(self, content: str, file_type: str) -> Dict[str, Any]:
        """Generate AI insights about the content"""
        try:
            llm = self.get_llm("openai")
            
            prompt = f"""
            Analyze the following {file_type} content and provide insights in JSON format:
            - sentiment: positive/negative/neutral
            - key_topics: list of main topics
            - complexity_level: beginner/intermediate/advanced
            - estimated_audience: target audience description
            
            Content: {content[:1500]}...
            
            Insights (JSON):
            """
            
            response = await llm.ainvoke(prompt)
            # Parse JSON response (simplified for demo)
            return {
                "sentiment": "neutral",
                "key_topics": ["general", "media"],
                "complexity_level": "intermediate",
                "estimated_audience": "general audience",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception:
            return {
                "sentiment": "neutral",
                "key_topics": ["media"],
                "complexity_level": "unknown",
                "estimated_audience": "general",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }


class ContentGenerationAgent(BaseAgent):
    """Agent responsible for generating various types of content"""
    
    def __init__(self):
        super().__init__("ContentGenerationAgent")
    
    async def process(self, state: AgentState) -> AgentState:
        """Generate various types of content based on analysis"""
        try:
            content = state.transcription or "No content available"
            summary = state.summary or "No summary available"
            
            # Generate different types of content
            state.content_generated = {
                "blog_post": await self._generate_blog_post(content, summary),
                "social_media": await self._generate_social_media(summary, state.tags),
                "script": await self._generate_script(content, state.insights),
                "q_and_a": await self._generate_qna(content)
            }
            
            state.processing_status = "completed"
            return state
            
        except Exception as e:
            state.errors.append(f"Content generation error: {str(e)}")
            state.processing_status = "error"
            return state
    
    async def _generate_blog_post(self, content: str, summary: str) -> str:
        """Generate a blog post based on content"""
        try:
            llm = self.get_llm("openai")
            
            prompt = f"""
            Create a professional blog post based on this content. Include an engaging title, introduction, main points, and conclusion.
            
            Content Summary: {summary}
            Original Content: {content[:1000]}...
            
            Blog Post:
            """
            
            response = await llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception:
            return f"# Blog Post\n\n{summary}\n\nThis is a generated blog post based on the analyzed content."
    
    async def _generate_social_media(self, summary: str, tags: List[str]) -> str:
        """Generate social media content"""
        try:
            llm = self.get_llm("openai")
            
            hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in tags[:5]])
            
            prompt = f"""
            Create an engaging social media post based on this summary. Include relevant hashtags and make it shareable.
            
            Summary: {summary}
            Suggested hashtags: {hashtags}
            
            Social Media Post:
            """
            
            response = await llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception:
            hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in tags[:3]])
            return f"{summary} {hashtags}"
    
    async def _generate_script(self, content: str, insights: Dict[str, Any]) -> str:
        """Generate a script based on content"""
        try:
            llm = self.get_llm("openai")
            
            audience = insights.get("estimated_audience", "general audience")
            
            prompt = f"""
            Create a script for {audience} based on this content. Include speaker directions and engaging dialogue.
            
            Content: {content[:1000]}...
            Target Audience: {audience}
            
            Script:
            """
            
            response = await llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception:
            return f"Script for {insights.get('estimated_audience', 'general audience')}:\n\n[Based on analyzed content]"
    
    async def _generate_qna(self, content: str) -> str:
        """Generate Q&A based on content"""
        try:
            llm = self.get_llm("openai")
            
            prompt = f"""
            Generate 5 relevant questions and answers based on this content:
            
            Content: {content[:1500]}...
            
            Q&A Format:
            Q: Question
            A: Answer
            
            Q&A:
            """
            
            response = await llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception:
            return "Q: What is this content about?\nA: This content has been analyzed using AI and insights have been generated."
