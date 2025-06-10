# Dec207Hub Backend Data Models
# Pydantic 모델 및 데이터 스키마

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    model: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    user_message: str
    ai_response: str
    model: str
    response_time: float
    timestamp: str

class WebSocketMessage(BaseModel):
    """WebSocket 메시지 모델"""
    type: str  # 'chat', 'system', 'error'
    message: str
    model: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = []
    timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    server: str
    ollama: str
    timestamp: str
    active_connections: int

class ModelsResponse(BaseModel):
    """모델 목록 응답 모델"""
    models: List[str]
    default: str
    error: Optional[str] = None
