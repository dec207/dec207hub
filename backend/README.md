# Dec207Hub Backend 실행 가이드

## 🚀 빠른 시작

### 1단계: Python 가상환경 설정
```bash
# backend 폴더로 이동
cd D:\DeepSeek\workspace\Dec207Hub\backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
```

### 2단계: 의존성 설치
```bash
# requirements.txt 기반 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install fastapi uvicorn websockets httpx python-multipart
```

### 3단계: Ollama 서버 확인
```bash
# 별도 터미널에서 Ollama 서버 실행
ollama serve

# 모델 다운로드 (아직 안했다면)
ollama pull qwen3:7b
```

### 4단계: API 서버 실행
```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📍 엔드포인트

- **메인**: http://localhost:8000
- **상태 확인**: http://localhost:8000/health
- **API 문서**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## 🔧 환경 변수 (선택사항)

`.env` 파일 생성:
```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen3:7b
SERVER_PORT=8000
```

## 🐛 문제 해결

### Ollama 연결 오류
```bash
# Ollama 서버 상태 확인
ollama list

# Ollama 서비스 재시작
ollama serve
```

### 포트 충돌
```bash
# 다른 포트로 실행
uvicorn main:app --port 8001
```

### 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 패키지 설치
pip install fastapi uvicorn
```
