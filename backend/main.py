# Dec207Hub Backend Main Application
# FastAPI 메인 앱 및 엔드포인트

import os
import httpx
import uvicorn
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 로컬 모듈 임포트
from config import (
    OLLAMA_BASE_URL, DEFAULT_MODEL, SERVER_HOST, SERVER_PORT, LOG_LEVEL
)
from models import ChatRequest, ChatResponse, HealthResponse, ModelsResponse
from logger import chat_logger
from chat_handler import chat_with_ollama
from websocket_handler import websocket_endpoint, manager

# FastAPI 앱 생성
app = FastAPI(title="Dec207Hub API", version="1.0.0")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 엔드포인트 등록 (정적 파일보다 먼저)
app.websocket("/ws")(websocket_endpoint)

# frontend 디렉토리를 정적 파일로 서빙
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인"""
    try:
        # Ollama 서버 연결 테스트
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            ollama_status = "connected" if response.status_code == 200 else "disconnected"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
    
    return HealthResponse(
        server="running",
        ollama=ollama_status,
        timestamp=datetime.now().isoformat(),
        active_connections=len(manager.active_connections)
    )

@app.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """사용 가능한 Ollama 모델 목록"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return ModelsResponse(models=models, default=DEFAULT_MODEL)
            else:
                return ModelsResponse(
                    models=[], 
                    default=DEFAULT_MODEL,
                    error="Ollama 서버에 연결할 수 없습니다"
                )
    except Exception as e:
        return ModelsResponse(
            models=[], 
            default=DEFAULT_MODEL,
            error=f"모델 목록을 가져올 수 없습니다: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request_body: ChatRequest, request: Request):
    """REST API를 통한 채팅"""
    message = request_body.message
    model = request_body.model or DEFAULT_MODEL
    conversation_history = request_body.conversation_history or []
    
    if not message:
        return ChatResponse(
            user_message="",
            ai_response="메시지가 없습니다",
            model=model,
            response_time=0.0,
            timestamp=datetime.now().isoformat()
        )
    
    # 클라이언트 IP 추출
    user_ip = chat_logger.get_client_ip(request)
    
    # 사용자 메시지 로깅
    chat_logger.log_message(user_ip, "user", message)
    
    # AI 응답 생성 (대화 히스토리 포함)
    start_time = datetime.now()
    ai_response = await chat_with_ollama(message, model, conversation_history)
    response_time = (datetime.now() - start_time).total_seconds()
    
    # AI 응답 로깅
    chat_logger.log_message(user_ip, "assistant", ai_response, response_time, model)
    
    return ChatResponse(
        user_message=message,
        ai_response=ai_response,
        model=model,
        response_time=response_time,
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    print("🚀 Dec207Hub API 서버 시작 중...")
    print("📍 URL: http://192.168.0.7:8000")
    print("🔌 WebSocket: ws://192.168.0.7:8000/ws")
    print("📋 API 문서: http://192.168.0.7:8000/docs")
    print("📱 모바일 접속 지원: WebSocket 연결 가능")
    print(f"📝 채팅 로그 저장 위치: {chat_logger.log_dir}")
    print("=" * 60)
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level=LOG_LEVEL.lower())
