# Dec207Hub Backend WebSocket Handler
# WebSocket 연결 관리 및 실시간 채팅

import json
import hashlib
import logging
from datetime import datetime
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from logger import chat_logger
from chat_handler import chat_with_ollama
from config import DEFAULT_MODEL

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket 연결 관리 클래스"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """WebSocket 연결 수락"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 연결됨. 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """WebSocket 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket 연결 해제됨. 총 연결 수: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """개별 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")

    async def broadcast(self, message: str):
        """전체 브로드캐스트"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 실패: {e}")

# 전역 연결 매니저 인스턴스
manager = ConnectionManager()

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
            
            # 메시지 처리
            should_continue = await process_websocket_message(
                websocket, message_data, user_ip, processing_message, last_message_hash
            )
            
            if not should_continue[0]:  # 처리 중단
                continue
                
            processing_message, last_message_hash = should_continue[1], should_continue[2]
            
            try:
                user_message = message_data.get("message", "").strip()
                model = message_data.get("model", DEFAULT_MODEL)
                conversation_history = message_data.get("conversation_history", [])
                
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
                    "message_hash": last_message_hash  # 메시지 해시 반환
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

async def process_websocket_message(websocket: WebSocket, message_data: dict, 
                                   user_ip: str, processing_message: bool, 
                                   last_message_hash: str) -> tuple:
    """WebSocket 메시지 전처리 및 검증"""
    
    # 데이터 처리 및 유효성 검사
    message_type = message_data.get("type", "chat")  # 기본값은 chat
    user_message = message_data.get("message", "").strip()
    
    # 메시지 타입이 chat이 아니면 무시
    if message_type != "chat":
        logger.warning(f"알 수 없는 메시지 타입: {message_type}")
        return (False, processing_message, last_message_hash)
    
    # 메시지 중복 처리 방지 - 빈 메시지는 무시하지만 처리 중인 경우 대기
    if not user_message:
        return (False, processing_message, last_message_hash)
        
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
        return (False, processing_message, last_message_hash)
        
    # 동일한 메시지 중복 처리 방지 (해시 비교)
    message_hash = hashlib.md5(f"{user_message}_{datetime.now().strftime('%Y%m%d%H%M')}".encode()).hexdigest()
    if message_hash == last_message_hash:
        logger.warning(f"중복 메시지 무시: {user_message[:30]}...")
        return (False, processing_message, last_message_hash)
        
    # 처리 상태 플래그 설정
    processing_message = True
    last_message_hash = message_hash
    
    return (True, processing_message, last_message_hash)
