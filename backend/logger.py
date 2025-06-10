# Dec207Hub Backend Logging System
# 채팅 로거 및 세션 관리

import os
import logging
from datetime import datetime
from typing import Union
from fastapi import WebSocket, Request

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatLogger:
    """채팅 로그 관리 클래스"""
    
    def __init__(self, log_dir: str = "chat_logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            logger.info(f"✅ 채팅 로그 디렉토리 생성: {self.log_dir}")
    
    def get_client_ip(self, websocket_or_request: Union[WebSocket, Request]) -> str:
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
    
    def get_log_filename(self, user_ip: str) -> str:
        """로그 파일명 생성: YYYY-MM-DD_IP.txt"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        ip_clean = user_ip.replace(".", "_").replace(":", "_")
        return f"{date_str}_{ip_clean}.txt"
    
    def log_message(self, user_ip: str, role: str, content: str, 
                   response_time: float = None, model: str = None):
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

# 전역 로거 인스턴스
chat_logger = ChatLogger()
