# RTX 3070 최적화 설정
# 8GB VRAM 기준 최적화

import os

# RTX 3070 최적화 모델 설정
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"  # RTX 3070 최적 모델

# 백업 모델 (메모리 부족시)
FALLBACK_MODEL = "deepseek-coder:6.7b"

# 서버 설정
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# RTX 3070 메모리 최적화
GPU_MEMORY_FRACTION = 0.85  # VRAM의 85%만 사용
BATCH_SIZE = 1              # 배치 크기 최소화
MAX_TOKENS = 2048           # 토큰 수 제한

# Function Calling 활성화
ENABLE_MCP = True
ENABLE_FUNCTION_CALLING = True

# ABAP 개발 최적화 파라미터
AI_TEMPERATURE = 0.05       # 정확한 문법
AI_TOP_P = 0.9
AI_REPEAT_PENALTY = 1.1
AI_MAX_NEW_TOKENS = 1024    # 응답 길이 제한 (메모리 절약)

# 컨텍스트 관리 (메모리 효율적)
MAX_CONVERSATION_HISTORY = 10
MAX_CONTEXT_MESSAGES = 5
MAX_MESSAGE_LENGTH = 800

# 로그 설정
LOG_LEVEL = "INFO"
CHAT_LOG_DIR = "chat_logs"

# WebSocket 설정
WEBSOCKET_TIMEOUT = 60.0

# HTTP 클라이언트 설정
HTTP_TIMEOUT = 45.0

# RTX 3070 성능 모니터링
ENABLE_GPU_MONITORING = True
GPU_MEMORY_THRESHOLD = 7.5  # GB, 경고 임계값

# 캐시 설정 (메모리 절약)
ENABLE_MODEL_CACHE = True
CACHE_SIZE_MB = 512

print("🎮 RTX 3070 최적화 설정 로드됨")
print(f"📊 추천 모델: {DEFAULT_MODEL}")
print(f"🔧 백업 모델: {FALLBACK_MODEL}")
print(f"💾 최대 VRAM 사용: {GPU_MEMORY_FRACTION * 8:.1f}GB")
