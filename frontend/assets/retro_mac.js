/**
 * Dec207Hub - Retro Mac JavaScript Framework v3.0 (Modular)
 * AI 채팅 허브를 위한 레트로 Mac OS 스타일 웹 컴포넌트 라이브러리
 * Created by dec207 - 모듈화된 버전
 */

class Dec207Hub {
    constructor() {
        console.log('Dec207Hub 메인 스크립트 로드 및 초기화 시작...');
        this.version = '3.0';
        this.initialized = false;
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupAll();
            });
        } else {
            this.setupAll();
        }
    }

    async setupAll() {
        try {
            console.log('🚀 Dec207Hub 초기화 시작...');
            
            // 의존성 체크
            await this.checkDependencies();
            
            // 서브 시스템들 초기화
            this.initializeSubSystems();
            
            // 이벤트 리스너 설정
            this.setupEventListeners();
            
            // 완료 메시지
            this.showInitializationComplete();
            
            this.initialized = true;
            console.log('✅ Dec207Hub 초기화 완료!');
            
        } catch (error) {
            console.error('❌ Dec207Hub 초기화 실패:', error);
            this.showInitializationError(error);
        }
    }

    async checkDependencies() {
        const dependencies = [
            { name: 'DEC207_CONFIG', obj: window.DEC207_CONFIG },
            { name: 'DEMO_RESPONSES', obj: window.DEMO_RESPONSES },
            { name: 'uiComponents', obj: window.uiComponents },
            { name: 'voiceHandler', obj: window.voiceHandler },
            { name: 'websocketClient', obj: window.websocketClient },
            { name: 'chatSystem', obj: window.chatSystem }
        ];

        const missing = dependencies.filter(dep => !dep.obj);
        
        if (missing.length > 0) {
            const missingNames = missing.map(dep => dep.name).join(', ');
            throw new Error(`필수 의존성 누락: ${missingNames}`);
        }

        console.log('✅ 모든 의존성 확인됨');
    }

    initializeSubSystems() {
        // WebSocket 연결 시작
        if (window.websocketClient) {
            window.websocketClient.setupWebSocket();
        }

        console.log('✅ 서브 시스템 초기화 완료');
    }

    setupEventListeners() {
        // 메뉴 클릭 이벤트
        document.addEventListener('dec207-menu-click', (e) => {
            console.log('Menu clicked:', e.detail.menu);
            this.handleMenuAction(e.detail.menu);
        });

        // 버튼 클릭 이벤트
        document.addEventListener('dec207-button-click', (e) => {
            console.log('Button clicked:', e.detail.button.textContent);
            this.handleButtonAction(e.detail.button);
        });

        console.log('✅ 이벤트 리스너 설정 완료');
    }

    handleMenuAction(menuText) {
        switch (menuText.toLowerCase()) {
            case 'clear chat':
            case '채팅 기록 삭제':
                if (window.chatSystem) {
                    window.chatSystem.clearChatHistory();
                }
                break;
                
            case 'connect blender':
            case 'blender 연결':
                if (window.uiComponents) {
                    window.uiComponents.connectBlender();
                }
                break;
                
            case 'connect unity':
            case 'unity 연결':
                if (window.uiComponents) {
                    window.uiComponents.connectUnity();
                }
                break;
                
            case 'toggle theme':
            case '테마 변경':
                if (window.uiComponents) {
                    window.uiComponents.toggleTheme();
                }
                break;
                
            default:
                console.log('알 수 없는 메뉴 액션:', menuText);
        }
    }

    handleButtonAction(button) {
        const buttonText = button.textContent.toLowerCase().trim();
        const buttonClass = button.className;
        
        // 특정 버튼 액션 처리
        if (buttonClass.includes('voice-btn')) {
            // 음성 버튼은 voice_handler.js에서 처리됨
            return;
        }
        
        if (buttonClass.includes('primary') && buttonClass.includes('dec207-btn')) {
            // 전송 버튼은 chat_system.js에서 처리됨
            return;
        }
        
        // 기타 버튼 처리
        console.log('기타 버튼 액션:', buttonText);
    }

    showInitializationComplete() {
        console.log('Dec207Hub 시스템 준비 완료!');
        
        console.log(`
╔══════════════════════════════════════╗
║Dec207Hub v${this.version} Ready!     ║
║                                      ║
║  🤖 AI Chat System                   ║
║  🔌 WebSocket Client                 ║
║  🔊 Voice Handler                    ║
║  🎨 UI Components                    ║
║  ⚙️  Configuration                   ║
╚══════════════════════════════════════╝
        `);
    }

    showInitializationError(error) {
        console.error('💥 Dec207Hub 초기화 중 오류:', error);
        
        if (window.uiComponents) {
            window.uiComponents.showNotification(`초기화 오류: ${error.message}`, 5000);
        } else {
            alert(`Dec207Hub 초기화 실패: ${error.message}`);
        }
    }

    // ===== 공개 API 메서드 =====
    getStatus() {
        return {
            version: this.version,
            initialized: this.initialized,
            websocketConnected: window.websocketClient?.isConnected || false,
            ttsActive: window.voiceHandler?.isTTSActive() || false,
            messageCount: window.chatSystem?.conversationHistory?.length || 0
        };
    }

    reconnectWebSocket() {
        if (window.websocketClient) {
            window.websocketClient.manualReconnect();
        }
    }

    sendTestMessage(message = "안녕하세요! 테스트 메시지입니다.") {
        if (window.chatSystem) {
            window.Dec207Chat.sendMessage(message);
        }
    }

    toggleDebugMode() {
        document.body.classList.toggle('debug-mode');
        const isDebug = document.body.classList.contains('debug-mode');
        
        if (window.uiComponents) {
            window.uiComponents.showNotification(
                `디버그 모드 ${isDebug ? '활성화' : '비활성화'}`, 
                2000
            );
        }
        
        return isDebug;
    }
}

// ===== 전역 인스턴스 생성 =====
try {
    const dec207Hub = new Dec207Hub();
    window.dec207Hub = dec207Hub;
} catch (e) {
    console.error('Dec207Hub 인스턴스 생성 실패:', e);
    alert('Dec207Hub 로딩 중 치명적인 오류가 발생했습니다. 콘솔을 확인해주세요.');
}

// ===== 전역 헬퍼 함수 =====
window.Dec207Hub = {
    // 기본 기능
    getStatus: () => window.dec207Hub?.getStatus(),
    reconnect: () => window.dec207Hub?.reconnectWebSocket(),
    testMessage: (msg) => window.dec207Hub?.sendTestMessage(msg),
    toggleDebug: () => window.dec207Hub?.toggleDebugMode(),
    
    // UI 컨트롤
    showDialog: (options) => window.Dec207UI?.showDialog(options),
    showNotification: (message, duration) => window.Dec207UI?.showNotification(message, duration),
    toggleTheme: () => window.Dec207UI?.toggleTheme(),
    
    // 채팅 컨트롤
    clearChat: () => window.Dec207Chat?.clearChat(),
    sendMessage: (message) => window.Dec207Chat?.sendMessage(message),
    
    // MCP 연결
    connectBlender: () => window.Dec207UI?.connectBlender(),
    connectUnity: () => window.Dec207UI?.connectUnity()
};

// ===== 개발자 도구 =====
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.Dec207Dev = {
        config: () => window.DEC207_CONFIG,
        logs: () => console.log('Dec207Hub 로그는 브라우저 콘솔에서 확인하세요'),
        status: () => console.table(window.Dec207Hub.getStatus()),
        test: () => window.Dec207Hub.testMessage(),
        version: () => window.dec207Hub?.version || 'unknown'
    };
    
    console.log('🔧 개발자 도구 사용 가능: window.Dec207Dev');
}

console.log('Dec207Hub v3.0 모듈화 완료 - 안정성 및 확장성 개선');
