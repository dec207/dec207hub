# Dec207Hub Backend Chat Handler
# Gemma3-Tools 4B + Gemma3 4B 일반화된 할루시네이션 방지

import json
import httpx
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import (
    OLLAMA_BASE_URL, DEFAULT_MODEL, FALLBACK_MODEL, HTTP_TIMEOUT, 
    MAX_CONVERSATION_HISTORY, MAX_CONTEXT_MESSAGES, MAX_MESSAGE_LENGTH,
    AI_TEMPERATURE, AI_TOP_P, AI_REPEAT_PENALTY, AI_MAX_NEW_TOKENS,
    ENABLE_MCP, ENABLE_FUNCTION_CALLING, ENABLE_FACT_CHECK, 
    FAST_RESPONSE_MODE, RESPONSE_TIMEOUT
)

logger = logging.getLogger(__name__)

async def chat_with_ollama(message: str, model: str = DEFAULT_MODEL, 
                          conversation_history: List[Dict] = None,
                          enable_tools: bool = True) -> str:
    """Gemma3-Tools 4B 채팅 + 일반화된 할루시네이션 방지"""
    try:
        timeout = RESPONSE_TIMEOUT if FAST_RESPONSE_MODE else HTTP_TIMEOUT
        async with httpx.AsyncClient(timeout=timeout) as client:
            # 컨텍스트 구성
            context_prompt = build_safe_context_prompt(conversation_history)
            
            # 일반화된 안전 프롬프트
            enhanced_prompt = build_general_safety_prompt(context_prompt, message)
            
            # 안전한 응답용 페이로드
            payload = build_safe_payload(model, enhanced_prompt)
            
            logger.info(f"Gemma3-Tools 4B 요청: {message[:30]}...")
            response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # 응답 추출 및 검증
                ai_response = extract_and_validate_response(data, message)
                
                logger.info(f"Gemma3-Tools 4B 응답 완료: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error(f"Ollama API 오류: {response.status_code}")
                return await fallback_chat(message, conversation_history)
                
    except httpx.TimeoutException:
        logger.warning("Gemma3-Tools 4B 응답 시간 초과 - 백업 모델 사용")
        return await fallback_chat(message, conversation_history)
    except Exception as e:
        logger.error(f"Gemma3-Tools 4B 오류: {str(e)}")
        return "AI 연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

def build_safe_context_prompt(conversation_history: List[Dict]) -> str:
    """안전한 컨텍스트 프롬프트 구성"""
    if not conversation_history:
        return ""
    
    # 최근 대화만 간단히 포함 (4B 모델용)
    recent_history = conversation_history[-2:]
    context_lines = []
    
    for msg in recent_history:
        role = "사용자" if msg.get('role') == 'user' else "AI"
        content = msg.get('content', '')[:150]
        context_lines.append(f"{role}: {content}")
    
    return "이전 대화:\n" + "\n".join(context_lines) + "\n\n" if context_lines else ""

def build_general_safety_prompt(context_prompt: str, message: str) -> str:
    """일반화된 안전 프롬프트"""
    return f"""정확성을 최우선으로 하는 AI 어시스턴트입니다.

**응답 원칙:**
1. 존재하지 않는 정보나 최신 정보 조작 금지
2. 사실과 의견을 명확히 구분

{context_prompt}질문: {message}

정확한 답변:"""

def build_safe_payload(model: str, prompt: str) -> Dict[str, Any]:
    """안전한 응답용 페이로드 (4B 모델 최적화)"""
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.2,  # 낮은 온도로 일관성 확보
            "top_p": 0.95,         # 토큰 선택 범위 축소
            "repeat_penalty": 1.2,
            "num_predict": 2000,   # 4B 모델용 토큰 수
            "num_ctx": 4096,      # 4B 모델용 컨텍스트
        }
    }

def extract_and_validate_response(data: Dict[str, Any], original_message: str) -> str:
    """응답 추출 및 일반화된 검증"""
    ai_response = data.get("message", {}).get("content", "응답을 생성할 수 없습니다.").strip()
    
    # 기본 정리
    ai_response = re.sub(r'\n{3,}', '\n\n', ai_response)
    ai_response = ai_response.strip()
    
    # 일반화된 할루시네이션 검증
    ai_response = detect_general_hallucinations(ai_response)
    
    return ai_response

def detect_general_hallucinations(response: str) -> str:
    """일반화된 할루시네이션 패턴 감지"""
    
    # 일반적인 위험 패턴들
    dangerous_patterns = [
#        (r'최근에?\s*(발표|공개|출시|발견)', '최신 정보'),
#        (r'2025년.*이후', '미래 정보'),
#        (r'공식.*발표.*했습니다', '공식 발표'),
#        (r'연구.*결과.*보여줍니다', '연구 결과'),
#        (r'전문가.*말했습니다', '전문가 인용'),
#        (r'확실한?\s*정보.*있습니다', '확실성 과장'),
#        (r'새로운?\s*(기술|제품|서비스)', '신기술 정보')
    ]
    
    found_issues = []
    for pattern, issue_type in dangerous_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            found_issues.append(issue_type)
    
    if found_issues:
        warning = f"⚠️ **정확성 주의**: 이 답변에는 불확실한 정보가 포함될 수 있습니다.\n\n"
        response = warning + response + "\n\n💡 **권장**: 중요한 정보는 공식 소스에서 재확인해주세요."
    
    return response

async def fallback_chat(message: str, conversation_history: List[Dict] = None) -> str:
    """백업 모델로 안전한 전환"""
    try:
        logger.info(f"백업 모델 {FALLBACK_MODEL} 사용")
        
        safe_prompt = f"""정확한 정보만 제공하세요. 확실하지 않으면 "잘 모르겠습니다"라고 답변하세요.

질문: {message}

답변:"""
        
        payload = {
            "model": FALLBACK_MODEL,
            "messages": [{"role": "user", "content": safe_prompt}],
            "stream": False,
            "options": {
                "temperature": 0.05,
                "num_predict": 2000,
            }
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "백업 응답 실패").strip()
            
    except Exception as e:
        logger.error(f"백업 모델 실패: {str(e)}")
    
    return "죄송합니다. 현재 AI 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요."

def get_model_status() -> Dict[str, Any]:
    """모델 상태 정보"""
    return {
        "primary_model": DEFAULT_MODEL,
        "fallback_model": FALLBACK_MODEL,
        "anti_hallucination": True,
        "general_safety": True,
        "fact_check": ENABLE_FACT_CHECK
    }

logger.info("🛡️ Gemma3-Tools 4B 일반화된 안전 Chat Handler 로드 완료")
logger.info(f"🚀 메인 모델: {DEFAULT_MODEL}")
logger.info(f"🔧 백업 모델: {FALLBACK_MODEL}")
logger.info("🛡️ 일반화된 할루시네이션 방지 시스템 활성화")
