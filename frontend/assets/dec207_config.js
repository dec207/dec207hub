/**
 * Dec207Hub - Configuration and Constants
 * 설정 상수 및 전역 변수
 */

// 서버 설정
const DEC207_CONFIG = {
    // 서버 IP 설정 ('auto'로 설정하면 자동 감지)
    SERVER_IP: window.DEC207_SERVER_IP || 'auto',
    SERVER_PORT: 8000,
    
    // WebSocket 설정
    WEBSOCKET_TIMEOUT: 15000,
    
    // 채팅 설정
    MAX_HISTORY_LENGTH: 20,
    MAX_MESSAGE_LENGTH: 10000,
    
    // 음성 설정
    TTS_RATE: 0.9,
    TTS_PITCH: 1,
    TTS_LANG: 'ko-KR',
    
    // 알림 설정
    NOTIFICATION_DURATION: 3000,
    
    // 애니메이션 설정
    CLICK_ANIMATION_DURATION: 100,
    TYPING_DELAY_MIN: 1000,
    TYPING_DELAY_MAX: 2000,
    
    // UI 설정
    NOTIFICATION_STYLE: `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #000000;
        color: #ffffff;
        padding: 8px 16px;
        border: 2px solid #ffffff;
        font-family: 'VT323', monospace;
        font-size: 14px;
        z-index: 9999;
    `
};

// 데모 응답 목록
const DEMO_RESPONSES = [
    "안녕하세요! **Dec207Hub AI 어시스턴트**입니다.\n\n어떻게 도와드릴까요?",
    "흥미로운 질문이네요.\n\n더 자세히 설명해 주시겠어요?",
    "네, 이해했습니다.\n\n다른 질문이 있으시면 언제든 말씀해 주세요.",
    "**Dec207Hub의 MCP 연동 기능**을 통해 다음과 같은 도구들과 연결할 수 있습니다:\n\n- Blender 3D 모델링\n- Unity 게임 엔진\n- 파일 관리 시스템\n- 날씨 API 연동",
    "레트로 Mac OS 스타일이 마음에 드시나요? 🤖\n\n이 인터페이스는 **클래식 Mac 디자인**에서 영감을 받아 제작되었습니다."
];

// 전역 변수로 노출
window.DEC207_CONFIG = DEC207_CONFIG;
window.DEMO_RESPONSES = DEMO_RESPONSES;
