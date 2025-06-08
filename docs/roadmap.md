# Dec207Hub Development Roadmap

## 🎯 프로젝트 목표
웹기반 AI 채팅 데모서비스 구축 with MCP Integration

## 📅 개발 일정

### Week 1: 환경 설정 및 기초 구조
- [x] 프로젝트 폴더 구조 생성
- [ ] Ollama 설치 및 설정
- [ ] 기본 웹 서버 구축
- [ ] 첫 번째 채팅 UI 구현

### Week 2: AI 채팅 기능
- [ ] Ollama API 연동
- [ ] 실시간 채팅 구현
- [ ] TTS/STT 기능 추가
- [ ] 모바일 반응형 UI

### Week 3: MCP 서버 구축
- [ ] MCP 프로토콜 구현
- [ ] Blender MCP 서버 개발
- [ ] Unity MCP 서버 개발
- [ ] 도구 호출 시스템

### Week 4: 통합 및 최적화
- [ ] 전체 시스템 통합
- [ ] 성능 최적화
- [ ] 문서화 완료
- [ ] 데모 영상 제작

## 🔧 기술 스택 결정

### Frontend 선택
- **React.js** (추천) - 컴포넌트 재사용성, 생태계
- Vue.js - 학습 곡선, 가벼움
- Vanilla JS - 단순함, 빠른 개발

### UI 테마
- **Retro Mac OS** (채택) - 독특함, 레트로 감성
- Modern Dark - 트렌디, 개발자 친화적
- Minimal - 깔끔함, 성능

### Backend 선택
- **Python FastAPI** (추천) - Ollama 연동 용이, MCP 지원
- Node.js Express - JavaScript 통일, 빠른 개발
- Go Gin - 성능, 바이너리 배포

## 📋 체크리스트

### 환경 설정
- [ ] Git 레포지토리 생성
- [ ] Ollama 설치 확인
- [ ] Python/Node.js 환경 구성
- [ ] 개발 도구 설정 (VSCode, etc.)

### 개발 준비
- [ ] API 설계 문서 작성
- [ ] UI 와이어프레임 작성
- [ ] MCP 서버 스펙 정의
- [ ] 데이터베이스 스키마 설계

### 테스트 계획
- [ ] 유닛 테스트 설정
- [ ] 통합 테스트 계획
- [ ] 성능 테스트 시나리오
- [ ] 사용자 테스트 계획

## 🎨 UI/UX 가이드라인

### 디자인 철학
- **Retro-Futuristic**: 80년대 Mac OS 감성 + 현대적 기능
- **Developer-Friendly**: 개발자가 편안한 인터페이스
- **Multi-Platform**: 데스크톱과 모바일 동시 지원

### 색상 팔레트
- Primary: #000000 (Black)
- Secondary: #FFFFFF (White)
- Accent: #00FF00 (Green Terminal)
- Warning: #FFFF00 (Yellow)
- Error: #FF0000 (Red)

### 타이포그래피
- Main: VT323 (Monospace)
- Body: Monaco, Consolas
- Size: 14px base, responsive scaling

## 🚨 위험 요소 및 대응

### 기술적 위험
- **Ollama 성능**: GPU 메모리 부족 → 모델 크기 조절
- **MCP 복잡성**: 프로토콜 이해 부족 → 단계별 학습
- **WebRTC 호환성**: 브라우저 제한 → Fallback 구현

### 일정 위험
- **과도한 기능**: 범위 크리프 → MVP 우선 개발
- **학습 곡선**: 새 기술 적응 → 프로토타입 우선

## 📈 성공 지표

### 기술적 목표
- 응답 시간 < 3초
- 모바일 호환성 100%
- TTS/STT 정확도 > 90%
- MCP 연동 성공률 > 95%

### 사용자 경험
- 직관적인 UI/UX
- 안정적인 채팅 기능
- 3D 도구 연동 데모
- 개발자 문서 완성도

---

**다음 단계**: Ollama 설치 및 기본 웹 서버 구축
