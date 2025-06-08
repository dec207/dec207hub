# Dec207Hub Backend API Server
# FastAPI + Ollama 연동 서버

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import httpx
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any
import logging
import re
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dec207Hub API", version="1.0.0")

# CORS 설정 (프론트엔드 연결 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama 설정
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"  # 설치된 모델에 맞춤

# 연결된 WebSocket 클라이언트들
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 연결됨. 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket 연결 해제됨. 총 연결 수: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# 채팅 로거 클래스
class ChatLogger:
    def __init__(self, log_dir: str = "chat_logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            logger.info(f"✅ 채팅 로그 디렉토리 생성: {self.log_dir}")
    
    def get_client_ip(self, websocket_or_request):
        """클라이언트 IP 주소 추출"""
        try:
            if hasattr(websocket_or_request, 'client'):  # WebSocket
                return websocket_or_request.client.host
            elif hasattr(websocket_or_request, 'headers'):  # Request
                # X-Forwarded-For 헤더 확인 (프록시 환경)
                forwarded = websocket_or_request.headers.get('X-Forwarded-For')
                if forwarded:
                    return forwarded.split(',')[0].strip()
                # X-Real-IP 헤더 확인
                real_ip = websocket_or_request.headers.get('X-Real-IP')
                if real_ip:
                    return real_ip
                # 기본 클라이언트 IP
                return websocket_or_request.client.host
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"IP 주소 추출 중 오류 발생: {e}")
            return "unknown"
    
    def get_log_filename(self, user_ip: str):
        """로그 파일명 생성: YYYY-MM-DD_IP.txt"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        ip_clean = user_ip.replace(".", "_").replace(":", "_")
        return f"{date_str}_{ip_clean}.txt"
    
    def log_message(self, user_ip: str, role: str, content: str, response_time: float = None, model: str = None):
        """메시지 로깅"""
        filename = self.get_log_filename(user_ip)
        filepath = os.path.join(self.log_dir, filename)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        role_display = "사용자" if role == "user" else "AI" if role == "assistant" else "시스템"
        
        try:
            # 파일이 없으면 헤더 추가
            write_header = not os.path.exists(filepath)
            
            with open(filepath, 'a', encoding='utf-8') as f:
                if write_header:
                    f.write(f"=== Dec207Hub 채팅 로그 ===\n")
                    f.write(f"날짜: {datetime.now().strftime('%Y-%m-%d')}\n")
                    f.write(f"사용자 IP: {user_ip}\n")
                    f.write(f"서버: Dec207Hub API v1.0\n")
                    f.write("=" * 50 + "\n\n")
                
                f.write(f"[{timestamp}] {role_display}: {content}\n")
                if response_time:
                    f.write(f"    (응답시간: {response_time:.2f}초)\n")
                if model and role == "assistant":
                    f.write(f"    (모델: {model})\n")
                f.write("\n")
                
        except Exception as e:
            logger.error(f"❌ 로그 저장 실패: {e}")
    
    def log_session_event(self, user_ip: str, event: str):
        """세션 이벤트 로깅 (연결/해제 등)"""
        self.log_message(user_ip, "system", event)

# 채팅 로거 인스턴스 생성
chat_logger = ChatLogger()

# API 엔드포인트들
@app.get("/")
async def root():
    return {
        "message": "Dec207Hub API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    try:
        # Ollama 서버 연결 테스트
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            ollama_status = "connected" if response.status_code == 200 else "disconnected"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
    
    return {
        "server": "running",
        "ollama": ollama_status,
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections)
    }

@app.get("/models")
async def get_available_models():
    """사용 가능한 Ollama 모델 목록"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return {"models": models, "default": DEFAULT_MODEL}
            else:
                return {"error": "Ollama 서버에 연결할 수 없습니다", "models": [], "default": DEFAULT_MODEL}
    except Exception as e:
        return {"error": f"모델 목록을 가져올 수 없습니다: {str(e)}", "models": [], "default": DEFAULT_MODEL}

async def chat_with_ollama(message: str, model: str = DEFAULT_MODEL, conversation_history: List[Dict] = None) -> str:
    """채팅 프론트엔드에서 코드 포매팅을 지원하도록 Ollama와 채팅"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 대화 컨텍스트 구성 - 중복 방지 및 최적화
            context_prompt = ""
            if conversation_history and len(conversation_history) > 0:
                # 중복 메시지 제거 및 최근 4개 메시지만 사용 (성능 최적화)
                unique_history = []
                seen_messages = set()
                
                for msg in reversed(conversation_history[-8:]):  # 최근 8개에서 중복 제거
                    msg_content = msg.get('content', '').strip()
                    if msg_content and msg_content not in seen_messages:
                        unique_history.append(msg)
                        seen_messages.add(msg_content)
                        if len(unique_history) >= 4:  # 최대 4개만 유지
                            break
                
                if unique_history:
                    context_prompt = "이전 대화:\n"
                    for msg in reversed(unique_history):  # 시간순으로 정렬
                        role_display = "사용자" if msg.get('role') == 'user' else "AI"
                        content = msg.get('content', '')[:200]  # 내용 길이 제한
                        context_prompt += f"{role_display}: {content}\n"
                    context_prompt += "\n현재 질문에 집중하여 답변해주세요.\n\n"
            
            # 개선된 한국어 프롬프트 - 대화 연속성 지원
            enhanced_prompt = f"""당신은 한국어 AI 어시스턴트입니다. 다음 규칙을 따라 답변해주세요:

**답변 규칙:**
1. 반드시 한국어로만 답변
2. 정중한 언어 사용
3. 명확하고 도움이 되는 답변
4. 이전 대화 내용을 참고하여 자연스럽게 답변
5. 코드는 ```로 감싸서 작성
6. 중요한 내용은 **굵은 글씨**로 강조
7. 목록은 - 또는 1. 2. 3. 형식 사용
8. 과도한 특수기호 (★☆■●○ 등) 사용 금지

{context_prompt}현재 질문: {message}

AI 답변:"""
            
            payload = {
                "model": model,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 더 일관된 답변
                    "top_p": 0.9,
                    "max_tokens": 2000,
                    "repeat_penalty": 1.1
                }
            }
            
            logger.info(f"Ollama에 요청 전송: {message[:50]}...")
            response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "응답을 생성할 수 없습니다.").strip()
                
                # 답변 후처리: 기본적인 정리
                ai_response = clean_ai_response(ai_response)
                
                logger.info(f"Ollama 응답 받음: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error(f"Ollama API 오류: {response.status_code}")
                return f"AI 서버 오류가 발생했습니다. (상태 코드: {response.status_code})"
                
    except httpx.TimeoutException:
        logger.error("Ollama 응답 시간 초과")
        return "AI 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        logger.error(f"Ollama 통신 오류: {str(e)}")
        return f"AI 서버 연결 오류: {str(e)}"

def clean_ai_response(response: str) -> str:
    """기본적인 AI 응답 정리"""
    # 과도한 줄바꿈 제거
    response = response.replace('\n\n\n\n', '\n\n')
    
    # 시작/끝 공백 제거
    response = response.strip()
    
    # 과도한 특수기호 제거
    response = re.sub(r'[\u2605\u2606\u25a0\u25cf\u25cb\u2661\u2665\u2668\u266a\u266b]{2,}', '', response)
    
    return response

@app.post("/chat")
async def chat_endpoint(request_body: Dict[str, Any], request: Request):
    """REST API를 통한 채팅"""
    message = request_body.get("message", "")
    model = request_body.get("model", DEFAULT_MODEL)
    conversation_history = request_body.get("conversation_history", [])
    
    if not message:
        return {"error": "메시지가 없습니다"}
    
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
    
    return {
        "user_message": message,
        "ai_response": ai_response,
        "model": model,
        "response_time": response_time,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket을 통한 실시간 채팅 - 메시지 중복 방지 개선"""
    await manager.connect(websocket)
    
    # 클라이언트 IP 추출
    user_ip = chat_logger.get_client_ip(websocket)
    
    # 연결 로깅
    chat_logger.log_session_event(user_ip, f"WebSocket 세션 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"WebSocket 클라이언트 연결됨: {user_ip}")
    
    # 메시지 처리 상태 추적
    processing_message = False
    last_message_hash = None
    
    try:
        while True:
            # 클라이언트로부터 메시지 받기
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 데이터 처리 및 유효성 검사
            message_type = message_data.get("type", "chat")  # 기본값은 chat
            user_message = message_data.get("message", "").strip()
            model = message_data.get("model", DEFAULT_MODEL)
            conversation_history = message_data.get("conversation_history", [])
            
            # 메시지 타입이 chat이 아니면 무시
            if message_type != "chat":
                logger.warning(f"알 수 없는 메시지 타입: {message_type}")
                continue
            
            # 메시지 중복 처리 방지 - 빈 메시지는 무시하지만 처리 중인 경우 대기
            if not user_message:
                continue
                
            if processing_message:
                # 처리 중인 경우 대기 메시지 전송
                await manager.send_personal_message(
                    json.dumps({
                        "type": "system",
                        "message": "이전 메시지를 처리 중입니다. 잠시만 기다려주세요.",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                continue
                
            # 동일한 메시지 중복 처리 방지 (해시 비교)
            message_hash = hashlib.md5(f"{user_message}_{datetime.now().strftime('%Y%m%d%H%M')}".encode()).hexdigest()
            if message_hash == last_message_hash:
                logger.warning(f"중복 메시지 무시: {user_message[:30]}...")
                continue
                
            # 처리 상태 플래그 설정
            processing_message = True
            last_message_hash = message_hash
            
            try:
                logger.info(f"사용자 메시지 받음 ({user_ip}): {user_message[:50]}...")
                
                # 사용자 메시지 로깅
                chat_logger.log_message(user_ip, "user", user_message)
                
                # AI 응답 생성 (대화 히스토리 포함)
                start_time = datetime.now()
                ai_response = await chat_with_ollama(user_message, model, conversation_history)
                response_time = (datetime.now() - start_time).total_seconds()
                
                # AI 응답 로깅
                chat_logger.log_message(user_ip, "assistant", ai_response, response_time, model)
                
                # 클라이언트에게 AI 응답 전송
                response_data = {
                    "type": "chat_response",
                    "message": ai_response,
                    "model": model,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "message_hash": message_hash  # 메시지 해시 반환
                }
                
                await manager.send_personal_message(
                    json.dumps(response_data), 
                    websocket
                )
                
            except Exception as e:
                logger.error(f"메시지 처리 중 오류: {e}")
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": f"메시지 처리 오류: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
            finally:
                # 처리 완료 후 플래그 해제
                processing_message = False
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        chat_logger.log_session_event(user_ip, f"WebSocket 세션 종료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"클라이언트 연결 해제됨: {user_ip}")
    except Exception as e:
        logger.error(f"WebSocket 오류 ({user_ip}): {str(e)}")
        chat_logger.log_message(user_ip, "system", f"WebSocket 오류: {str(e)}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": f"서버 오류: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 
            websocket
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Dec207Hub API 서버 시작 중...")
    print("📍 URL: http://192.168.0.7:8000")
    print("🔌 WebSocket: ws://192.168.0.7:8000/ws")
    print("📋 API 문서: http://192.168.0.7:8000/docs")
    print("📱 모바일 접속 지원: WebSocket 연결 가능")
    print(f"📝 채팅 로그 저장 위치: {chat_logger.log_dir}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
