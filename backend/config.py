# Dec207Hub Backend Configuration
# Gemma3-Tools 4B + Gemma3 4B 고속 최적화 설정

import os

# ===== Ollama 설정 =====
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "orieg/gemma3-tools:4b-it-qat"   # 메인 모델 - 툴 기능 지원
FALLBACK_MODEL = "gemma3:4b"                     # 보조 모델 - 기본 응답용

# ===== 서버 설정 =====
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# ===== RTX 3070 고속 최적화 =====
GPU_MEMORY_LIMIT = 3.0  # GB, 4B 모델은 매우 효율적
ENABLE_GPU_MONITORING = True
GPU_MEMORY_THRESHOLD = 5.0  # GB, 경고 임계값

# ===== MCP & Function Calling 활성화 =====
ENABLE_MCP = True
ENABLE_FUNCTION_CALLING = True
MCP_TIMEOUT = 15.0  # 4B 모델 빠른 응답

# ===== SAP ABAP 개발 최적화 파라미터 (4B 튜닝) =====
AI_TEMPERATURE = 0.01       # 할루시네이션 방지를 위해 더 낮춤
AI_TOP_P = 0.9              
AI_REPEAT_PENALTY = 1.2     
AI_MAX_NEW_TOKENS = 1024    # 4B 모델 적정 길이

# ===== 컨텍스트 설정 (4B 모델 최적화) =====
MAX_CONVERSATION_HISTORY = 8    # 4B 모델에 적합한 크기
MAX_CONTEXT_MESSAGES = 4        # 컨텍스트 메시지 적정 수준
MAX_MESSAGE_LENGTH = 500        # 메시지 길이 적당히
CONTEXT_WINDOW = 8192           # 4B 모델 컨텍스트

# ===== 로그 설정 =====
LOG_LEVEL = "INFO"
CHAT_LOG_DIR = "chat_logs"

# ===== 네트워크 설정 (고속화) =====
WEBSOCKET_TIMEOUT = 25.0    # 단축
HTTP_TIMEOUT = 25.0         # 단축

# ===== 성능 최적화 (고속 응답) =====
BATCH_SIZE = 1              
CACHE_SIZE_MB = 256         # 4B 모델용 캐시
ENABLE_MODEL_CACHE = True   
FAST_RESPONSE_MODE = True   # 고속 응답 모드

# ===== ABAP 특화 설정 =====
ABAP_SYNTAX_CHECK = True    
ABAP_BEST_PRACTICES = True  
SAP_VERSION_SUPPORT = ["ECC", "S4HANA", "BTP"]

# ===== 할루시네이션 방지 설정 (간소화) =====
ENABLE_FACT_CHECK = True    
UNCERTAINTY_THRESHOLD = 0.5 # 4B 모델용 임계값
SAFETY_MODE = "balanced"    # 속도와 안전성 균형

# ===== 응답 속도 최적화 =====
ENABLE_STREAMING = False    # 스트리밍 비활성화로 안정성 확보
PARALLEL_PROCESSING = True  # 병렬 처리 활성화
RESPONSE_TIMEOUT = 20.0     # 응답 시간 제한

print("⚡ Gemma3-Tools 4B + Gemma3 4B 고속 최적화 설정 로드됨")
print(f"🚀 메인 모델: {DEFAULT_MODEL} (툴 기능 지원)")
print(f"🔧 보조 모델: {FALLBACK_MODEL} (기본 응답)")
print(f"💾 GPU 메모리 사용: ~{GPU_MEMORY_LIMIT}GB (매우 효율적)")
print(f"⚡ 고속 모드: {'활성화' if FAST_RESPONSE_MODE else '비활성화'}")
print(f"🛠️ Function Calling: {'활성화' if ENABLE_FUNCTION_CALLING else '비활성화'}")
