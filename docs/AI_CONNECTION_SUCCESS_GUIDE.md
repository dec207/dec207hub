# Dec207Hub AI 연결 성공 가이드

## ✅ 성공 케이스 진행 상태

### 🎯 **목표 달성**
- ❌ 시뮬레이션 데모 → ✅ 실제 AI 연결
- ❌ "DEMO MODE" → ✅ "AI CONNECTED"
- ❌ 가짜 응답 → ✅ 실제 llama3.1:8b AI 응답

### 📊 **현재 시스템 구성**
```
Frontend (브라우저)
    ↕ WebSocket (ws://localhost:8000/ws)
Backend (FastAPI 서버)
    ↕ HTTP API (http://localhost:11434)
Ollama (AI 엔진)
    ↕ Model: llama3.1:8b
```

---

## 🛠️ 전체 설정 및 실행 방법

### **사전 요구사항**
- Windows 10/11
- Python 3.8 이상
- Git (선택사항)
- 최신 브라우저 (Chrome/Edge 권장)

---

## 📦 1단계: Ollama 설치 및 설정

### Ollama 설치
1. **공식 사이트**: https://ollama.ai/download
2. **Windows용 인스톨러** 다운로드 및 설치
3. **설치 확인**:
   ```bash
   ollama --version
   ```

### AI 모델 다운로드
```bash
# llama3.1:8b 모델 다운로드 (약 4.9GB)
ollama pull llama3.1:8b

# 설치된 모델 확인
ollama list
```

### Ollama 서버 실행
```bash
# 터미널 창 1번에서 실행 (항상 켜두기)
ollama serve
```

**💡 중요**: 이 창은 계속 열어두고 닫지 마세요!

---

## 🐍 2단계: 백엔드 API 서버 설정

### Python 패키지 설치
```bash
# 터미널 창 2번에서 실행
cd D:\DeepSeek\workspace\Dec207Hub\backend

# 필수 패키지 설치
pip install fastapi uvicorn websockets httpx python-multipart

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

### 백엔드 서버 실행
```bash
# backend 폴더에서 실행
python main.py
```

**성공 메시지**:
```
🚀 Dec207Hub API 서버 시작 중...
📍 URL: http://localhost:8000
🔌 WebSocket: ws://localhost:8000/ws
📋 API 문서: http://localhost:8000/docs
```

### 서버 상태 확인
브라우저에서 접속: http://localhost:8000/health

**정상 응답**:
```json
{
  "server": "running",
  "ollama": "connected",
  "timestamp": "2025-06-01T23:10:52.756961",
  "active_connections": 0
}
```

---

## 🌐 3단계: 프론트엔드 실행

### VSCode Live Server 방법 (권장)
1. **VSCode** 실행
2. **확장(Extensions)** 탭에서 "Live Server" 검색
3. **"Live Server by Ritwick Dey"** 설치
4. `D:\DeepSeek\workspace\Dec207Hub` 폴더 열기
5. `frontend/index.html` 우클릭 → **"Open with Live Server"**
6. 자동으로 브라우저에서 열림

### 직접 파일 열기 방법
1. 파일 탐색기에서 `D:\DeepSeek\workspace\Dec207Hub\frontend\index.html`
2. 더블클릭하여 브라우저에서 열기

---

## 🔌 4단계: AI 연결 확인

### 연결 성공 시 나타나는 변화들

#### 1. **상태 표시 변경**
- 좌측 상단: **"DEMO MODE"** → **"AI CONNECTED"**
- 상태 표시등: **🔴 빨간색** → **🟢 초록색**

#### 2. **연결 알림**
```
"실제 AI 서버에 연결되었습니다! 🤖"
```

#### 3. **WebSocket 연결 수 증가**
http://localhost:8000/health 에서:
```json
"active_connections": 1  // 0에서 1로 증가
```

### AI 채팅 테스트
```
입력: "안녕하세요, 당신은 누구인가요?"
```

**데모 모드**: 미리 정해진 6개 응답 중 랜덤
**AI 연결 모드**: llama3.1:8b의 실제 AI 응답

---

## 🔧 라이브러리 및 의존성

### 백엔드 Python 패키지
```bash
# 필수 패키지
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install websockets==12.0
pip install httpx==0.25.2
pip install python-multipart==0.0.6

# 선택 패키지
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.1
pip install loguru==0.7.2
```

### 프론트엔드 (브라우저 기본 API 사용)
- Web Speech API (STT/TTS)
- WebSocket API
- 외부 라이브러리 없음

---

## 📋 실행 체크리스트

### 시작 전 확인사항
- [ ] Ollama 설치됨 (`ollama --version`)
- [ ] Python 설치됨 (`python --version`)
- [ ] VSCode 설치됨 (Live Server용)

### 실행 순서
1. [ ] **터미널 1**: `ollama serve` 실행
2. [ ] **터미널 2**: `cd backend` → `python main.py` 실행
3. [ ] **브라우저**: http://localhost:8000/health 상태 확인
4. [ ] **VSCode**: Live Server로 `frontend/index.html` 실행
5. [ ] **연결 확인**: "AI CONNECTED" 상태 확인
6. [ ] **테스트**: 실제 AI 채팅 시도

---

## 🚨 문제 해결

### Ollama 연결 실패
```bash
# Ollama 재시작
ollama serve

# 모델 재다운로드
ollama pull llama3.1:8b
```

### 백엔드 서버 오류
```bash
# 패키지 재설치
pip install --upgrade fastapi uvicorn

# 포트 변경
uvicorn main:app --port 8001
```

### 프론트엔드 연결 실패
- 브라우저 **F5** 새로고침
- 개발자 도구(F12) → Console 탭에서 오류 확인
- Live Server 재시작

### WebSocket 연결 오류
- 방화벽 설정 확인
- localhost:8000 포트 사용 여부 확인
- HTTPS 필요시 Live Server 사용

---

## 🎯 성공 기준

### ✅ **완전 성공 상태**
1. **Ollama**: `ollama list`에서 llama3.1:8b 확인
2. **백엔드**: http://localhost:8000/health에서 "connected"
3. **프론트엔드**: "AI CONNECTED" 표시
4. **채팅**: 실제 AI 응답 확인

### 📊 **성능 지표**
- **응답 시간**: 1-5초 (모델 크기에 따라)
- **메모리 사용**: ~6GB (llama3.1:8b)
- **연결 안정성**: WebSocket 지속 연결

---

## 📈 다음 단계 (향후 개발)

### Phase 1: 현재 완료 ✅
- [x] 레트로 Mac OS UI
- [x] 실제 AI 연결 (llama3.1:8b)
- [x] WebSocket 실시간 통신
- [x] 음성 인식/출력

### Phase 2: 진행 예정
- [ ] MCP 서버 구축 (Blender/Unity 연동)
- [ ] 다중 모델 지원
- [ ] 채팅 히스토리 저장
- [ ] 성능 최적화

### Phase 3: 고도화
- [ ] Docker 배포
- [ ] 클라우드 연동
- [ ] 플러그인 시스템
- [ ] 모바일 앱

---

**🎉 축하합니다! Dec207Hub AI 채팅 시스템이 성공적으로 구축되었습니다!**

이제 완전히 프라이빗한 환경에서 실제 AI와 채팅할 수 있습니다. 🤖✨
